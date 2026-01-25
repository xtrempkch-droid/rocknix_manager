#!/usr/bin/env python3
# rocknix_manager_v3.py
# Solução "Ultimate" para Rocknix:
# - Suporte a 50+ Sistemas
# - Identificação por Hex/Header (Deep Inspection)
# - Auto-Discovery de Rede
# - Gestão de Extensões sem Conflitos
# - Auditoria de BIOS com HASH CHECK (MD5)

import sys
import os
import subprocess
import shutil
import time
import socket
import hashlib
import tempfile
import struct
import platform
import threading
from pathlib import Path
from datetime import datetime
import zipfile
import io

# Dependências opcionais
try:
    import paramiko
except ImportError:
    paramiko = None

# Verificação de Dependência Crítica
try:
    import requests
except ImportError:
    print("ERRO: A biblioteca 'requests' não está instalada. Execute: pip install requests")
    sys.exit(1)

from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout,
                             QWidget, QLabel, QProgressBar, QFileDialog, QTextEdit,
                             QHBoxLayout, QLineEdit, QTableWidget, QTableWidgetItem,
                             QHeaderView, QRadioButton, QComboBox, QMessageBox, QDialog,
                             QCheckBox, QGridLayout, QScrollArea, QDialogButtonBox, QGroupBox)
from PyQt6.QtCore import QThread, pyqtSignal, Qt

# ------------------------------
# 1. Banco de Dados "Master" do Rocknix
# ------------------------------

# Configuração de Extensões Preferenciais
EXTENSAO_PREFERENCIAL = {
    'nes': '.nes', 'snes': '.sfc', 'n64': '.z64', 'gc': '.rvz', 'wii': '.wbfs',
    'wiiu': '.wua', 'gb': '.gb', 'gbc': '.gbc', 'gba': '.gba', 'nds': '.nds',
    '3ds': '.3ds', 'virtualboy': '.vb', 'pokemonmini': '.min',
    'mastersystem': '.sms', 'megadrive': '.md', 'sega32x': '.32x', 'segacd': '.chd',
    'saturn': '.iso', 'dreamcast': '.cdi', 'gamegear': '.gg', 'sg1000': '.sg',
    'psx': '.pbp', 'ps2': '.iso', 'psp': '.cso', 'psvita': '.zip',
    'atari2600': '.a26', 'atari5200': '.a52', 'atari7800': '.a78',
    'atarijaguar': '.j64', 'atarilynx': '.lnx',
    'arcade': '.zip', 'neogeo': '.zip', 'cps1': '.zip', 'cps2': '.zip',
    'cps3': '.zip', 'mame': '.zip', 'fbneo': '.zip', 'atomiswave': '.zip',
    'naomi': '.zip', 'amiga': '.lha', 'c64': '.d64', 'msx': '.rom',
    'zxspectrum': '.tzx', 'amstradcpc': '.dsk', 'dos': '.zip', 'x68000': '.dim',
    '3do': '.iso', 'pce': '.pce', 'pcecd': '.cue', 'colecovision': '.col',
    'intellivision': '.int', 'vectrex': '.vec', 'wonderswan': '.ws',
    'wonderswancolor': '.wsc', 'neogeopocket': '.ngp', 'neogeopocketcolor': '.ngc',
    'pico8': '.p8.png', 'tic80': '.tic'
}

# Mapa de Pastas
MAPA_ROCKNIX_FOLDER = {
    'nes': 'nes', 'snes': 'snes', 'n64': 'n64', 'gc': 'gc', 'wii': 'wii',
    'wiiu': 'wiiu', 'gb': 'gb', 'gbc': 'gbc', 'gba': 'gba', 'nds': 'nds',
    '3ds': '3ds', 'pokemonmini': 'pokemonmini', 'virtualboy': 'virtualboy',
    'mastersystem': 'mastersystem', 'megadrive': 'megadrive', 'sega32x': 'sega32x',
    'segacd': 'segacd', 'saturn': 'saturn', 'dreamcast': 'dreamcast',
    'gamegear': 'gamegear', 'sg1000': 'sg1000', 'psx': 'psx', 'ps2': 'ps2',
    'psp': 'psp', 'psvita': 'psvita', 'atari2600': 'atari2600',
    'atari5200': 'atari5200', 'atari7800': 'atari7800', 'atarijaguar': 'atarijaguar',
    'atarilynx': 'atarilynx', 'arcade': 'arcade', 'neogeo': 'neogeo',
    'cps1': 'cps1', 'cps2': 'cps2', 'cps3': 'cps3', 'mame': 'mame',
    'fbneo': 'fbneo', 'atomiswave': 'atomiswave', 'naomi': 'naomi',
    'amiga': 'amiga', 'c64': 'c64', 'msx': 'msx', 'zxspectrum': 'zxspectrum',
    'amstradcpc': 'amstradcpc', 'dos': 'dos', 'x68000': 'x68000', '3do': '3do',
    'pce': 'pcengine', 'pcecd': 'pcenginecd', 'colecovision': 'colecovision',
    'intellivision': 'intellivision', 'vectrex': 'vectrex', 'wonderswan': 'wonderswan',
    'wonderswancolor': 'wonderswancolor', 'neogeopocket': 'neogeopocket',
    'neogeopocketcolor': 'neogeopocketcolor', 'pico8': 'pico8', 'tic80': 'tic80'
}

# ------------------------------
# DATABASE DE BIOS (HASHES MD5)
# ------------------------------
BIOS_DATABASE = {
    # --- SONY ---
    'scph5500.bin': {'md5': '8dd7d5296a650fac7319bce665a6a53c', 'sys': 'PS1 (JP)', 'desc': 'Obrigatória para jogos JP'},
    'scph5501.bin': {'md5': '490f666e1afb15b7362b406ed1cea246', 'sys': 'PS1 (US)', 'desc': 'Obrigatória para jogos US'},
    'scph5502.bin': {'md5': '32736f17079d0b2b7024407c39ad3050', 'sys': 'PS1 (EU)', 'desc': 'Obrigatória para jogos EU'},
    'psxonpsp660.bin': {'md5': 'c53ca5908936d412331790f4426c6c33', 'sys': 'PS1 (PSP)', 'desc': 'Melhor performance (DuckStation)'},
    'scph39001.bin': {'md5': 'd5ce2c7d119f563ce04bc04dbc3a323e', 'sys': 'PS2 (US)', 'desc': 'Compatível PCSX2/Play!'},
    
    # --- SEGA ---
    'bios_CD_U.bin': {'md5': '2efd743390ffad365a45330c6a463c61', 'sys': 'Sega CD (US)', 'desc': 'Modelo 1 v1.10'},
    'bios_CD_E.bin': {'md5': 'e66fa1dc5820d254611fdcdba0662372', 'sys': 'Sega CD (EU)', 'desc': 'Modelo 1 v1.10'},
    'bios_CD_J.bin': {'md5': '278a93da838174dadabe39d897c51591', 'sys': 'Sega CD (JP)', 'desc': 'Modelo 1 v1.00'},
    'saturn_bios.bin': {'md5': 'af58e0fd19355465bcde8a00508933b9', 'sys': 'Saturn (JP)', 'desc': 'Bios Padrão Saturn'},
    'mpr-17933.bin': {'md5': '3240872c70984b6cbfda1586cab68dbe', 'sys': 'Saturn (US/EU)', 'desc': 'Alternativa comum'},
    'dc_boot.bin': {'md5': 'e10c53c2f8b90bab96ead2d368858623', 'sys': 'Dreamcast', 'desc': 'Bootloader'},
    'dc_flash.bin': {'md5': '0a93f7940c455902bea6e392dfde92a4', 'sys': 'Dreamcast', 'desc': 'Flash (Region Free)'},
    'naomi.zip': {'md5': 'VARIES', 'sys': 'Naomi Arcade', 'desc': 'Arquivo ZIP do MAME/FBNeo'},
    'awbios.zip': {'md5': 'VARIES', 'sys': 'Atomiswave', 'desc': 'Bios Atomiswave'},

    # --- NINTENDO ---
    'gba_bios.bin': {'md5': 'a860e8c0b6ec573d1e1e61f1bc566d7f', 'sys': 'GBA', 'desc': 'Game Boy Advance Boot'},
    'bios7.bin': {'md5': 'df692a80a5b1bc3129f3c163e596ba93', 'sys': 'NDS', 'desc': 'ARM7 BIOS'},
    'bios9.bin': {'md5': 'a392174eb3e572fed6c453309e67250a', 'sys': 'NDS', 'desc': 'ARM9 BIOS'},
    'firmware.bin': {'md5': 'e45033d9c0fa367bf1609fe794715278', 'sys': 'NDS', 'desc': 'Firmware (Opcional)'},
    'disksys.rom': {'md5': 'ca30b6d9c025f6e804f58f7004f98d78', 'sys': 'Famicom Disk', 'desc': 'FDS BIOS'},
    
    # --- ARCADE / SNK ---
    'neogeo.zip': {'md5': 'VARIES', 'sys': 'Neo Geo', 'desc': 'Essencial! Use set FBNeo/MAME recente'},
    'panafz10.bin': {'md5': '51f2f43ae2f3508a14d9f54597e2d365', 'sys': '3DO', 'desc': 'Panasonic FZ-10'},
    'goldstar.bin': {'md5': '92bd8942200701b223067eb0155a3062', 'sys': '3DO', 'desc': 'Goldstar Model'},

    # --- COMPUTADORES ---
    'kick34005.A500': {'md5': '854084365796a5b51f0f443836173d32', 'sys': 'Amiga 500', 'desc': 'Kickstart 1.3'},
    'kick40068.A1200': {'md5': '646773759326fbac3a2311fdc8cfef39', 'sys': 'Amiga 1200', 'desc': 'Kickstart 3.1'},
    'syscard3.pce': {'md5': '38179df8f4d9d9a936d102a3a24b3d74', 'sys': 'PC Engine CD', 'desc': 'System Card 3.0'},
    'msx2.rom': {'md5': 'ec1657490d292425510b64d8a1c6a084', 'sys': 'MSX2', 'desc': 'Japonesa'},
    'keropi.rom': {'md5': '2f78326a575c755c06495df0240d43a6', 'sys': 'X68000', 'desc': 'IPL ROM'}
}

# ------------------------------
# 2. Motor de Identificação (Deep Inspection)
# ------------------------------
class SystemDetector:
    @staticmethod
    def identificar_sistema(filepath):
        try:
            with open(filepath, 'rb') as f:
                header = f.read(32768)

            if len(header) > 0x108 and b'SEGA' in header[0x100:0x108]: return 'megadrive'
            if b'SEGA SEGASATURN' in header: return 'saturn'
            if b'SEGA SEGAKATANA' in header: return 'dreamcast'
            
            if len(header) > 4:
                if header[0:4] in [b'\x80\x37\x12\x40', b'\x40\x12\x37\x80', b'\x37\x80\x40\x12']: return 'n64'
            if header[0:4] == b'NES\x1a': return 'nes'
            
            nintendo_logo = b'\xCE\xED\x66\x66\xCC\x0D\x00\x0B'
            if len(header) > 0x110 and nintendo_logo in header[0x104:0x114]:
                if header[0x143] in [0x80, 0xC0]: return 'gbc'
                return 'gb'
            if len(header) > 0xB0 and header[0x04:0x0A] == b'\x24\xFF\xAE\x51\x69\x9A': return 'gba'

            if b'PLAYSTATION' in header or b'Sony Computer Entertainment' in header: return 'psx'
            if header[0x8000:0x8004] == b'PSP ' or header[0:4] == b'CISO': return 'psp'

            if len(header) > 0x200 and len(header) % 8192 == 512: return 'pce'
            if b'\xAA\x55' in header[:2] and b'COLECO' in header: return 'colecovision'

        except Exception:
            pass
        
        ext = Path(filepath).suffix.lower()
        ext_map = {
            '.smc': 'snes', '.sfc': 'snes', '.gen': 'megadrive', '.md': 'megadrive', '.bin': 'megadrive',
            '.nes': 'nes', '.z64': 'n64', '.n64': 'n64', '.iso': 'ps2', '.pbp': 'psx', '.cso': 'psp',
            '.rvz': 'gc', '.wbfs': 'wii', '.wua': 'wiiu', '.gba': 'gba', '.gbc': 'gbc', '.gb': 'gb',
            '.nds': 'nds', '.sms': 'mastersystem', '.gg': 'gamegear', '.a26': 'atari2600',
            '.zip': 'arcade', '.lha': 'amiga', '.d64': 'c64', '.rom': 'msx', '.pce': 'pce',
            '.ws': 'wonderswan', '.wsc': 'wonderswancolor', '.ngc': 'neogeopocketcolor',
            '.ngp': 'neogeopocket', '.p8': 'pico8', '.tic': 'tic80'
        }
        return ext_map.get(ext, 'desconhecido')

# ------------------------------
# 3. Network Discovery
# ------------------------------
class NetworkScanner(QThread):
    found_signal = pyqtSignal(str)
    log_signal = pyqtSignal(str)

    def run(self):
        self.log_signal.emit("🔍 Varrendo rede...")
        for host in ['ROCKNIX', 'ROCKNIX.local', 'JELOS', 'JELOS.local']:
            try:
                ip = socket.gethostbyname(host)
                self.found_signal.emit(ip)
                return
            except socket.error: pass

        local_ip = self.get_local_ip()
        if local_ip:
            base_ip = '.'.join(local_ip.split('.')[:-1])
            self.log_signal.emit(f"Varrendo IP: {base_ip}.x")
            valid_ips = []
            threads = []
            
            def check_ip(ip_end):
                target = f"{base_ip}.{ip_end}"
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.3)
                if s.connect_ex((target, 22)) == 0 or s.connect_ex((target, 445)) == 0:
                    valid_ips.append(target)
                s.close()

            for i in range(1, 255):
                t = threading.Thread(target=check_ip, args=(i,))
                threads.append(t)
                t.start()
            for t in threads: t.join()

            if valid_ips:
                self.found_signal.emit(valid_ips[0])
            else:
                self.log_signal.emit("❌ Nenhum dispositivo.")

    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception: IP = '127.0.0.1'
        finally: s.close()
        return IP

# ------------------------------
# 4. Workers (Scan/Envio)
# ------------------------------
class WorkerScan(QThread):
    progresso_sinal = pyqtSignal(int)
    log_sinal = pyqtSignal(str)
    item_encontrado = pyqtSignal(str, str, str)
    concluido_sinal = pyqtSignal()

    def __init__(self, pasta):
        super().__init__()
        self.origem = Path(pasta)

    def run(self):
        arquivos = [f for f in self.origem.iterdir() if f.is_file()]
        if not arquivos:
            self.log_sinal.emit("ℹ️ Pasta vazia.")
            self.concluido_sinal.emit()
            return
        
        self.log_sinal.emit("🧬 Analisando DNA...")
        for i, f in enumerate(arquivos):
            if f.stat().st_size < 1024 or f.suffix.lower() in ['.txt', '.nfo', '.xml', '.dat']: continue
            sistema = SystemDetector.identificar_sistema(f)
            if sistema == 'desconhecido' and f.suffix == '.zip': sistema = 'arcade' 
            if sistema != 'desconhecido': self.item_encontrado.emit(str(f), f.stem, sistema)
            self.progresso_sinal.emit(int(((i+1)/len(arquivos))*100))
        self.concluido_sinal.emit()

class WorkerEnvio(QThread):
    log_sinal = pyqtSignal(str)
    progresso_sinal = pyqtSignal(int)
    concluido_sinal = pyqtSignal(bool)

    def __init__(self, lista, destino, compactar_lista, modo_rede, ip):
        super().__init__()
        self.lista = lista
        self.destino_sd = destino
        self.compactar_lista = compactar_lista
        self.modo_rede = modo_rede
        self.ip = ip

    def run(self):
        dest_root = self.obter_ponto_montagem()
        if not dest_root:
            self.log_sinal.emit("❌ Erro: Destino inacessível.")
            self.concluido_sinal.emit(False)
            return

        target_base = dest_root
        if "roms" not in str(target_base).lower() and (target_base / "roms").exists():
             target_base = target_base / "roms"
        
        self.log_sinal.emit(f"📂 Destino: {target_base}")
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            for i, (orig_path, sys_name, nome_base) in enumerate(self.lista):
                try:
                    orig = Path(orig_path)
                    folder_name = MAPA_ROCKNIX_FOLDER.get(sys_name, 'roms')
                    target_folder = target_base / folder_name
                    target_folder.mkdir(parents=True, exist_ok=True)

                    ext_padrao = EXTENSAO_PREFERENCIAL.get(sys_name, orig.suffix)
                    nome_final = f"{nome_base}{ext_padrao}"
                    arquivo_para_enviar = orig

                    if sys_name in self.compactar_lista:
                        safe_to_zip = ['snes', 'megadrive', 'nes', 'gba', 'gb', 'gbc', 'nds', 'mastersystem', 'sega32x', 'arcade', 'neogeo', 'fbneo', 'mame', 'pce', 'msx', 'dos', 'atari2600']
                        
                        if sys_name in safe_to_zip:
                            nome_final = f"{nome_base}.zip"
                            arquivo_zip = temp_path / nome_final
                            if orig.suffix.lower() in ['.zip', '.7z']: arquivo_para_enviar = orig
                            else:
                                self.log_sinal.emit(f"📦 Compactando {nome_base}...")
                                with zipfile.ZipFile(arquivo_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
                                    zf.write(orig, arcname=f"{nome_base}{orig.suffix}")
                                arquivo_para_enviar = arquivo_zip
                        else:
                            if orig.suffix != ext_padrao: self.log_sinal.emit(f"📝 Renomeando {orig.suffix} -> {ext_padrao}")

                    dest_path = target_folder / nome_final
                    self.log_sinal.emit(f"🚀 {nome_final}")
                    shutil.copy2(arquivo_para_enviar, dest_path)

                except Exception as e: self.log_sinal.emit(f"⚠️ Erro {nome_base}: {e}")
                self.progresso_sinal.emit(int(((i+1)/len(self.lista))*100))
        self.concluido_sinal.emit(True)

    def obter_ponto_montagem(self):
        if not self.modo_rede: return Path(self.destino_sd) if self.destino_sd else None
        if shutil.which("gio"):
            try: subprocess.run(["gio", "mount", f"smb://{self.ip}/roms"], capture_output=True, check=False)
            except: pass
        base_run = Path(f"/run/user/{os.getuid()}/gvfs/") if hasattr(os, "getuid") else None
        if base_run and base_run.exists():
            for p in base_run.iterdir():
                if self.ip in p.name or self.ip.replace(':','_') in p.name: return p
        return None

# ------------------------------
# 5. BIOS AUDITOR (MD5 + SSH/Local)
# ------------------------------
class BiosAuditor(QThread):
    log_sinal = pyqtSignal(str)
    concluido_sinal = pyqtSignal(bool)
    item_checked = pyqtSignal(str, str, str) # Nome, Status, Cor

    def __init__(self, ip=None, folder=None, user='root', pwd='linux'):
        super().__init__()
        self.ip = ip
        self.folder = Path(folder) if folder else None
        self.user = user
        self.pwd = pwd

    def run(self):
        self.log_sinal.emit("🔎 Iniciando Auditoria Completa de BIOS (Hash MD5)...")
        
        # Modo Remoto (SSH)
        if self.ip:
            if not paramiko:
                self.log_sinal.emit("❌ Biblioteca 'paramiko' necessária para auditoria remota.")
                self.concluido_sinal.emit(False)
                return
            self._audit_remote()
        
        # Modo Local (SD Card)
        elif self.folder:
            self._audit_local()
        
        self.concluido_sinal.emit(True)

    def _calc_md5_local(self, fpath):
        hash_md5 = hashlib.md5()
        try:
            with open(fpath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except: return None

    def _audit_local(self):
        # Lista arquivos na pasta local
        local_files = {f.name: f for f in self.folder.iterdir() if f.is_file()}
        
        for bios_name, data in BIOS_DATABASE.items():
            if bios_name in local_files:
                self.log_sinal.emit(f"⏳ Verificando {bios_name}...")
                calc_md5 = self._calc_md5_local(local_files[bios_name])
                
                if data['md5'] == 'VARIES':
                    self.item_checked.emit(bios_name, f"PRESENTE (Zip: {data['sys']})", "orange")
                elif calc_md5 == data['md5']:
                    self.item_checked.emit(bios_name, f"OK ({data['sys']})", "green")
                else:
                    self.item_checked.emit(bios_name, f"ERRO HASH ({data['sys']})", "red")
            else:
                self.item_checked.emit(bios_name, f"FALTANDO ({data['sys']})", "red")

    def _audit_remote(self):
        try:
            self.log_sinal.emit(f"🔌 Conectando SSH em {self.ip}...")
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.ip, username=self.user, password=self.pwd, timeout=5)
            
            # Tenta localizar pasta de BIOS
            bios_path = "/storage/roms/bios"
            stdin, stdout, stderr = ssh.exec_command(f"ls {bios_path}")
            remote_files = stdout.read().decode().splitlines()
            
            for bios_name, data in BIOS_DATABASE.items():
                if bios_name in remote_files:
                    if data['md5'] == 'VARIES':
                         self.item_checked.emit(bios_name, f"PRESENTE (Zip: {data['sys']})", "orange")
                    else:
                        # Executa md5sum remotamente (MUITO mais rápido que baixar)
                        cmd = f"md5sum {bios_path}/{bios_name}"
                        stdin, out, err = ssh.exec_command(cmd)
                        res = out.read().decode().strip().split()[0]
                        
                        if res == data['md5']:
                            self.item_checked.emit(bios_name, f"OK ({data['sys']})", "green")
                        else:
                            self.item_checked.emit(bios_name, f"ERRO HASH ({data['sys']})", "red")
                else:
                    self.item_checked.emit(bios_name, f"FALTANDO ({data['sys']})", "red")
            
            ssh.close()
            
        except Exception as e:
            self.log_sinal.emit(f"❌ Erro SSH: {e}")


# ------------------------------
# 6. Interface Gráfica
# ------------------------------
class RocknixGui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.compactar_lista = ['snes', 'megadrive', 'nes', 'gba', 'gb', 'gbc', 'nds', 'mastersystem', 'sega32x', 'arcade', 'neogeo', 'atari2600', 'pce']
        self.destino_sd = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("ROCKNIX Manager V4 - BIOS Ultimate")
        self.setMinimumSize(1100, 800)
        self.setStyleSheet("""
            QMainWindow { background-color: #222; color: #eee; font-family: 'Segoe UI', sans-serif; }
            QGroupBox { border: 1px solid #444; margin-top: 10px; font-weight: bold; color: #aaa; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }
            QTableWidget { background-color: #333; color: #fff; gridline-color: #555; border: none; }
            QHeaderView::section { background-color: #444; padding: 5px; border: 1px solid #555; }
            QPushButton { background-color: #0d47a1; color: white; padding: 8px 15px; border-radius: 4px; border: none; }
            QPushButton:hover { background-color: #1976d2; }
            QPushButton:disabled { background-color: #555; color: #888; }
            QLineEdit { padding: 8px; background-color: #444; color: white; border: 1px solid #555; border-radius: 4px; }
            QTextEdit { background-color: #111; color: #00e676; font-family: Consolas, monospace; border: 1px solid #444; }
            QProgressBar { text-align: center; border: 1px solid #444; border-radius: 4px; height: 20px; }
            QProgressBar::chunk { background-color: #00e676; }
        """)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        # --- Topo ---
        gb_conn = QGroupBox("1. Conexão")
        layout_conn = QHBoxLayout()
        self.rb_rede = QRadioButton("Wi-Fi / Rede")
        self.rb_rede.setChecked(True)
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("IP (ex: 192.168.1.10)")
        btn_detect = QPushButton("📡 Auto-Detectar")
        btn_detect.clicked.connect(self.detectar_dispositivo)
        self.rb_sd = QRadioButton("Cartão SD")
        btn_browse_sd = QPushButton("📂 Selecionar")
        btn_browse_sd.clicked.connect(self.selecionar_sd)
        layout_conn.addWidget(self.rb_rede)
        layout_conn.addWidget(self.ip_input)
        layout_conn.addWidget(btn_detect)
        layout_conn.addSpacing(30)
        layout_conn.addWidget(self.rb_sd)
        layout_conn.addWidget(btn_browse_sd)
        gb_conn.setLayout(layout_conn)
        main_layout.addWidget(gb_conn)

        # --- Ações ---
        layout_actions = QHBoxLayout()
        self.btn_config = QPushButton("⚙️ Configurar Compressão")
        self.btn_config.clicked.connect(self.configurar_compressao)
        layout_actions.addWidget(self.btn_config)
        layout_actions.addStretch()
        main_layout.addLayout(layout_actions)

        # --- Tabela ROMS ---
        self.tabela = QTableWidget(0, 4)
        self.tabela.setHorizontalHeaderLabels(["Enviar", "Arquivo", "Sistema (DNA)", "Destino"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela.verticalHeader().setVisible(False)
        main_layout.addWidget(self.tabela)

        # --- Tabela BIOS ---
        self.tbl_bios = QTableWidget(0, 3)
        self.tbl_bios.setHorizontalHeaderLabels(["BIOS", "Status / Sistema", "Descrição"])
        self.tbl_bios.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tbl_bios.setVisible(False) # Escondido até clicar em verificar
        main_layout.addWidget(self.tbl_bios)

        # --- Footer ---
        layout_footer = QHBoxLayout()
        log_layout = QVBoxLayout()
        self.log_area = QTextEdit()
        self.log_area.setFixedHeight(100)
        self.progress = QProgressBar()
        log_layout.addWidget(self.log_area)
        log_layout.addWidget(self.progress)
        
        btns_layout = QVBoxLayout()
        self.btn_scan = QPushButton("🔍 2. Ler ROMs")
        self.btn_scan.setMinimumHeight(40)
        self.btn_scan.clicked.connect(self.scan_roms)
        self.btn_enviar = QPushButton("🚀 3. Enviar ROMs")
        self.btn_enviar.setMinimumHeight(40)
        self.btn_enviar.setEnabled(False)
        self.btn_enviar.clicked.connect(self.enviar_arquivos)
        self.btn_bios = QPushButton("🧬 Verificar BIOS (Hash)")
        self.btn_bios.setMinimumHeight(40)
        self.btn_bios.setStyleSheet("background-color: #4a148c; color: white;")
        self.btn_bios.clicked.connect(self.verificar_bios)
        
        btns_layout.addWidget(self.btn_scan)
        btns_layout.addWidget(self.btn_enviar)
        btns_layout.addWidget(self.btn_bios)
        
        layout_footer.addLayout(log_layout, stretch=3)
        layout_footer.addLayout(btns_layout, stretch=1)
        main_layout.addLayout(layout_footer)

    def detectar_dispositivo(self):
        self.scanner = NetworkScanner()
        self.scanner.log_signal.connect(self.log_area.append)
        self.scanner.found_signal.connect(lambda ip: self.ip_input.setText(ip))
        self.scanner.start()

    def selecionar_sd(self):
        d = QFileDialog.getExistingDirectory(self, "Raiz SD/ROMS")
        if d:
            self.destino_sd = d
            self.rb_sd.setChecked(True)
            self.log_area.append(f"📂 Local: {d}")

    def configurar_compressao(self):
        d = QDialog(self)
        d.setWindowTitle("Sistemas para Zipar")
        d.setMinimumSize(600, 400)
        l = QVBoxLayout(d)
        area = QScrollArea()
        w = QWidget()
        g = QGridLayout(w)
        sistemas = sorted(list(MAPA_ROCKNIX_FOLDER.keys()))
        checks = {}
        for i, s in enumerate(sistemas):
            cb = QCheckBox(s.upper())
            if s in self.compactar_lista: cb.setChecked(True)
            checks[s] = cb
            g.addWidget(cb, i // 4, i % 4)
        area.setWidget(w)
        area.setWidgetResizable(True)
        l.addWidget(area)
        bbox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        bbox.accepted.connect(d.accept)
        bbox.rejected.connect(d.reject)
        l.addWidget(bbox)
        if d.exec(): self.compactar_lista = [s for s, c in checks.items() if c.isChecked()]

    def scan_roms(self):
        self.tabela.setVisible(True)
        self.tbl_bios.setVisible(False)
        p = QFileDialog.getExistingDirectory(self, "Pasta Origem")
        if not p: return
        self.tabela.setRowCount(0)
        self.worker_scan = WorkerScan(p)
        self.worker_scan.log_sinal.connect(self.log_area.append)
        self.worker_scan.progresso_sinal.connect(self.progress.setValue)
        self.worker_scan.item_encontrado.connect(self.add_rom_row)
        self.worker_scan.concluido_sinal.connect(lambda: self.btn_enviar.setEnabled(True))
        self.worker_scan.start()

    def add_rom_row(self, path, nome, sistema):
        r = self.tabela.rowCount()
        self.tabela.insertRow(r)
        ck = QTableWidgetItem()
        ck.setCheckState(Qt.CheckState.Checked)
        self.tabela.setItem(r, 0, ck)
        self.tabela.setItem(r, 1, QTableWidgetItem(Path(path).name))
        item_sys = QTableWidgetItem(sistema.upper())
        item_sys.setForeground(Qt.GlobalColor.red if sistema == 'desconhecido' else Qt.GlobalColor.green)
        self.tabela.setItem(r, 2, item_sys)
        cb = QComboBox()
        cb.addItems(sorted(list(MAPA_ROCKNIX_FOLDER.keys())))
        idx = cb.findText(sistema)
        cb.setCurrentIndex(idx if idx >= 0 else 0)
        self.tabela.setCellWidget(r, 3, cb)

    def enviar_arquivos(self):
        lista = []
        for i in range(self.tabela.rowCount()):
            if self.tabela.item(i, 0).checkState() == Qt.CheckState.Checked:
                orig_name = self.tabela.item(i, 1).text()
                full = self.worker_scan.origem / orig_name
                sys_sel = self.tabela.cellWidget(i, 3).currentText()
                lista.append((full, sys_sel, full.stem))
        if not lista: return
        ip = self.ip_input.text()
        if self.rb_rede.isChecked() and not ip:
            QMessageBox.warning(self, "IP", "Defina IP.")
            return
        self.worker_envio = WorkerEnvio(lista, self.destino_sd, self.compactar_lista, self.rb_rede.isChecked(), ip)
        self.worker_envio.log_sinal.connect(self.log_area.append)
        self.worker_envio.progresso_sinal.connect(self.progress.setValue)
        self.worker_envio.concluido_sinal.connect(lambda: QMessageBox.information(self, "Fim", "Concluído!"))
        self.worker_envio.start()

    def verificar_bios(self):
        self.tabela.setVisible(False)
        self.tbl_bios.setVisible(True)
        self.tbl_bios.setRowCount(0)
        
        if self.rb_rede.isChecked():
            ip = self.ip_input.text()
            if not ip:
                QMessageBox.warning(self, "Erro", "Necessário IP.")
                return
            self.auditor = BiosAuditor(ip=ip)
        else:
            if not self.destino_sd:
                QMessageBox.warning(self, "Erro", "Selecione SD.")
                return
            d = Path(self.destino_sd)
            if "bios" not in str(d): d = d / "bios"
            self.auditor = BiosAuditor(folder=d)
            
        self.auditor.log_sinal.connect(self.log_area.append)
        self.auditor.item_checked.connect(self.add_bios_row)
        self.auditor.start()

    def add_bios_row(self, nome, status, cor):
        r = self.tbl_bios.rowCount()
        self.tbl_bios.insertRow(r)
        self.tbl_bios.setItem(r, 0, QTableWidgetItem(nome))
        
        it_status = QTableWidgetItem(status)
        if cor == "green": it_status.setForeground(Qt.GlobalColor.green)
        elif cor == "red": it_status.setForeground(Qt.GlobalColor.red)
        elif cor == "orange": it_status.setForeground(Qt.GlobalColor.yellow)
        self.tbl_bios.setItem(r, 1, it_status)
        
        desc = BIOS_DATABASE.get(nome, {}).get('desc', '')
        self.tbl_bios.setItem(r, 2, QTableWidgetItem(desc))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = RocknixGui()
    w.show()
    sys.exit(app.exec())
