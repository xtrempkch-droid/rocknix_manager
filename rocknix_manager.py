#!/usr/bin/env python3
import sys
import os
import subprocess
import shutil
import time
import hashlib
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERRO: 'requests' não instalado. Execute: pip install requests")
    sys.exit(1)

from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                             QWidget, QLabel, QProgressBar, QFileDialog, QTextEdit, 
                             QHBoxLayout, QLineEdit, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QRadioButton, QComboBox, QMessageBox, QDialog, 
                             QCheckBox, QGridLayout, QScrollArea, QDialogButtonBox)
from PyQt6.QtCore import QThread, pyqtSignal, Qt

# --- Configurações ---
LIBRETRO_DAT_URL = "https://raw.githubusercontent.com/libretro/libretro-database/master/metadat/no-intro/"

MAPA_LIBRETRO_DAT = {
    '.nes': 'Nintendo - Nintendo Entertainment System',
    '.sfc': 'Nintendo - Super Nintendo Entertainment System',
    '.smc': 'Nintendo - Super Nintendo Entertainment System',
    '.gba': 'Nintendo - Game Boy Advance',
    '.gb': 'Nintendo - Game Boy',
    '.gbc': 'Nintendo - Game Boy Color',
    '.md': 'Sega - Mega Drive - Genesis',
    '.sms': 'Sega - Master System - Mark III',
    '.v64': 'Nintendo - Nintendo 64', '.z64': 'Nintendo - Nintendo 64',
    '.pce': 'NEC - PC Engine - TurboGrafx 16', '.nds': 'Nintendo - Nintendo DS',
    '.bin': 'Sony - PlayStation', '.cue': 'Sony - PlayStation', 
    '.iso': 'Sony - PlayStation Portable', '.gdi': 'Sega - Dreamcast', '.cdi': 'Sega - Dreamcast'
}

MAPA_ROCKNIX_FOLDER = {
    '.nes': 'nes', '.sfc': 'snes', '.smc': 'snes', '.gba': 'gba', 
    '.gb': 'gb', '.gbc': 'gbc', '.md': 'megadrive', '.sms': 'mastersystem', 
    '.v64': 'n64', '.z64': 'n64', '.pce': 'pcengine', '.nds': 'nds', 
    '.bin': 'psx', '.cue': 'psx', '.chd': 'psx', '.iso': 'ps2', 
    '.cso': 'psp', '.zip': 'arcade', '.7z': 'arcade', '.gdi': 'dreamcast', '.cdi': 'dreamcast'
}

SISTEMAS_PARA_CHD = ['psx', 'ps2', 'dreamcast', 'saturn', 'gc', 'psp', 'atomiswave']
SISTEMAS_DISPONIVEIS = sorted(list(set(list(MAPA_ROCKNIX_FOLDER.values()))))

class RomDatabase:
    def __init__(self):
        self.db_hash = {}
        self.cache_dir = Path.home() / ".rocknix_manager_cache"
        self.cache_dir.mkdir(exist_ok=True)

    def preparar_sistema(self, ext):
        dat_name = MAPA_LIBRETRO_DAT.get(ext)
        if not dat_name: return False
        local_path = self.cache_dir / f"{dat_name}.dat"
        if not local_path.exists():
            try:
                r = requests.get(f"{LIBRETRO_DAT_URL}{dat_name.replace(' ', '%20')}.dat", timeout=10)
                if r.status_code == 200:
                    with open(local_path, "wb") as f: f.write(r.content)
            except: return False
        return self._parse_dat(local_path)

    def _parse_dat(self, path):
        self.db_hash = {}
        try:
            tree = ET.parse(path)
            for game in tree.getroot().findall('game'):
                desc = game.find('description').text if game.find('description') is not None else game.get('name')
                for rom in game.findall('rom'):
                    sha1 = rom.get('sha1')
                    if sha1: self.db_hash[sha1.lower()] = desc
            return True
        except: return False

    def identificar(self, file_path):
        sha1 = hashlib.sha1()
        try:
            with open(file_path, "rb") as f:
                while chunk := f.read(65536): sha1.update(chunk)
            return self.db_hash.get(sha1.hexdigest().lower())
        except: return None

class WorkerScan(QThread):
    progresso_sinal = pyqtSignal(int); log_sinal = pyqtSignal(str)
    item_encontrado = pyqtSignal(str, str, str); concluido_sinal = pyqtSignal()

    def __init__(self, pasta):
        super().__init__(); self.origem = Path(pasta); self.db = RomDatabase()

    def run(self):
        arquivos = [f for f in self.origem.iterdir() if f.suffix.lower() in MAPA_ROCKNIX_FOLDER]
        if arquivos: self.db.preparar_sistema(arquivos[0].suffix.lower())
        for i, f in enumerate(arquivos):
            nome = self.db.identificar(f)
            self.item_encontrado.emit(str(f), nome if nome else f.stem, MAPA_ROCKNIX_FOLDER.get(f.suffix.lower(), 'arcade'))
            self.progresso_sinal.emit(int(((i+1)/len(arquivos))*100))
        self.concluido_sinal.emit()

class WorkerEnvio(QThread):
    log_sinal = pyqtSignal(str); progresso_sinal = pyqtSignal(int); concluido_sinal = pyqtSignal(bool)

    def __init__(self, lista, destino, compactar, modo_rede, ip):
        super().__init__()
        self.lista = lista; self.destino_sd = destino; self.compactar = compactar
        self.modo_rede = modo_rede; self.ip = ip

    def run(self):
        dest_root = self.obter_ponto_montagem()
        if not dest_root:
            self.log_sinal.emit("❌ Erro: Destino não encontrado."); self.concluido_sinal.emit(False); return

        target_base = dest_root
        if "games-external" in dest_root.name or "games-internal" in dest_root.name:
            target_base = dest_root / "roms"

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            for i, (orig, sys, nome) in enumerate(self.lista):
                try:
                    ext = orig.suffix
                    if sys in self.compactar:
                        ext = ".chd" if sys in SISTEMAS_PARA_CHD else ".zip"
                    
                    final_name = f"{nome}{ext}"
                    arq_pronto = self.preparar_local(orig, temp_path, sys, final_name)
                    
                    self.log_sinal.emit(f"🚀 Enviando: {final_name}")
                    target_folder = target_base / sys
                    target_folder.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(arq_pronto, target_folder / final_name)
                except Exception as e: self.log_sinal.emit(f"⚠️ Erro: {str(e)}")
                self.progresso_sinal.emit(int(((i+1)/len(self.lista))*100))
        self.concluido_sinal.emit(True)

    def obter_ponto_montagem(self):
        if not self.modo_rede: return Path(self.destino_sd) if self.destino_sd else None
        for s in ["roms", "games-roms", "games-external", "games-internal"]:
            subprocess.run(["gio", "mount", "-a", f"smb://{self.ip}/{s}"], capture_output=True)
        base = Path(f"/run/user/{os.getuid()}/gvfs/")
        for _ in range(5):
            if base.exists():
                for p in base.iterdir():
                    if self.ip in p.name: return p
            time.sleep(1)
        return None

    def preparar_local(self, origem, temp, sistema, nome_final):
        saida = temp / nome_final
        if sistema in self.compactar:
            if sistema in SISTEMAS_PARA_CHD and origem.suffix.lower() in ['.iso', '.cue', '.bin', '.gdi', '.cdi']:
                if shutil.which("chdman"):
                    subprocess.run(["chdman", "createcd", "-i", str(origem), "-o", str(saida)], check=True, capture_output=True)
                    return saida
            elif origem.suffix.lower() not in ['.zip', '.7z', '.chd']:
                if shutil.which("7z"):
                    subprocess.run(["7z", "a", "-tzip", str(saida), str(origem)], stdout=subprocess.DEVNULL, check=True)
                    return saida
        return origem

class RocknixGui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.compactar_lista = [s for s in SISTEMAS_DISPONIVEIS if s != 'arcade']
        self.setWindowTitle("ROCKNIX Manager v0.1 - Start Edition")
        self.setMinimumSize(1000, 700)
        self.init_ui()

    def init_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Top Bar
        top = QHBoxLayout()
        self.rb_rede = QRadioButton("Rede (IP)"); self.rb_rede.setChecked(True)
        self.ip_input = QLineEdit(); self.ip_input.setPlaceholderText("IP do Console")
        self.rb_sd = QRadioButton("SD Local")
        top.addWidget(self.rb_rede); top.addWidget(self.ip_input); top.addWidget(self.rb_sd); top.addStretch()
        layout.addLayout(top)

        # Table
        self.tabela = QTableWidget(0, 4)
        self.tabela.setHorizontalHeaderLabels(["V", "Arquivo", "Nome Real", "Sistema"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabela)

        # Log & Progress
        self.log_area = QTextEdit(readOnly=True); self.log_area.setFixedHeight(100)
        layout.addWidget(self.log_area)
        self.progress = QProgressBar(); layout.addWidget(self.progress)

        # Buttons
        bot = QHBoxLayout()
        btn_scan = QPushButton("📂 Scan ROMs"); btn_scan.clicked.connect(self.scan)
        btn_go = QPushButton("🚀 Iniciar"); btn_go.clicked.connect(self.enviar)
        bot.addWidget(btn_scan); bot.addWidget(btn_go)
        layout.addLayout(bot)

    def scan(self):
        p = QFileDialog.getExistingDirectory(self, "ROMs")
        if p:
            self.tabela.setRowCount(0)
            self.worker_scan = WorkerScan(p)
            self.worker_scan.item_encontrado.connect(self.add_table)
            self.worker_scan.start()

    def add_table(self, path, nome, sys):
        r = self.tabela.rowCount(); self.tabela.insertRow(r)
        ck = QTableWidgetItem(); ck.setCheckState(Qt.CheckState.Checked); self.tabela.setItem(r, 0, ck)
        self.tabela.setItem(r, 1, QTableWidgetItem(Path(path).name))
        self.tabela.setItem(r, 2, QTableWidgetItem(nome))
        cb = QComboBox(); cb.addItems([s.upper() for s in SISTEMAS_DISPONIVEIS]); cb.setCurrentText(sys.upper())
        self.tabela.setCellWidget(r, 3, cb)

    def enviar(self):
        if not hasattr(self, 'worker_scan'): return
        lista = []
        for i in range(self.tabela.rowCount()):
            if self.tabela.item(i, 0).checkState() == Qt.CheckState.Checked:
                lista.append((self.worker_scan.origem / self.tabela.item(i, 1).text(), 
                              self.tabela.cellWidget(i, 3).currentText().lower(), 
                              self.tabela.item(i, 2).text()))
        self.worker_env = WorkerEnvio(lista, None, self.compactar_lista, self.rb_rede.isChecked(), self.ip_input.text())
        self.worker_env.log_sinal.connect(self.log_area.append)
        self.worker_env.start()

if __name__ == "__main__":
    app = QApplication(sys.argv); w = RocknixGui(); w.show(); sys.exit(app.exec())
