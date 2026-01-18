import os
import re
import shutil
import socket
import customtkinter as ctk
from tkinter import filedialog, messagebox
from zeroconf import Zeroconf, ServiceBrowser
from datetime import datetime

# --- CONFIGURAÇÕES VISUAIS ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class RocknixDiscovery:
    def __init__(self, callback):
        self.callback = callback
        self.zeroconf = Zeroconf()
        self.browser = ServiceBrowser(self.zeroconf, "_workstation._tcp.local.", self)

    def add_service(self, zc, type_, name):
        if "rocknix" in name.lower() or "anbernic" in name.lower():
            info = zc.get_service_info(type_, name)
            if info:
                ip = socket.inet_ntoa(info.addresses[0])
                self.callback(name.split('.')[0], ip)

class RocknixGamerManager(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ROCKNIX ROM COMMANDER - v1.0")
        self.geometry("1200x800")

        # Variáveis de Estado e Configurações
        self.local_path = ""
        self.remote_path = ""
        self.arquivos_locais = []
        self.arquivos_remotos = []
        self.dispositivos = {}
        
        # Variáveis de Configuração (Toggles)
        self.cfg_auto_rename = ctk.BooleanVar(value=True)
        self.cfg_check_space = ctk.BooleanVar(value=True)
        self.cfg_show_log = ctk.BooleanVar(value=True)

        self.setup_ui()
        self.discovery = RocknixDiscovery(self.on_device_found)

    def setup_ui(self):
        # Barra Superior
        self.top_bar = ctk.CTkFrame(self, height=80, fg_color="#1a1a1a")
        self.top_bar.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(self.top_bar, text="DISPOSITIVO:", font=("Arial", 12, "bold")).pack(side="left", padx=10)
        self.device_combo = ctk.CTkComboBox(self.top_bar, values=["Procurando..."], command=self.connect_to_device)
        self.device_combo.pack(side="left", padx=5)

        ctk.CTkLabel(self.top_bar, text="SISTEMA:", font=("Arial", 12, "bold")).pack(side="left", padx=20)
        self.sys_combo = ctk.CTkComboBox(self.top_bar, values=["snes", "megadrive", "psx", "gba", "n64", "bios"])
        self.sys_combo.pack(side="left", padx=5)

        self.btn_settings = ctk.CTkButton(self.top_bar, text="⚙", width=40, fg_color="#333", command=self.open_settings)
        self.btn_settings.pack(side="right", padx=10)

        # Container Principal (Dual Pane)
        self.panes = ctk.CTkFrame(self, fg_color="transparent")
        self.panes.pack(fill="both", expand=True, padx=10)

        # Painel Esquerdo (PC)
        self.left_pane = ctk.CTkFrame(self.panes, border_width=2, border_color="#00ffff")
        self.left_pane.pack(side="left", fill="both", expand=True, padx=5)
        
        ctk.CTkLabel(self.left_pane, text="📁 PC LOCAL", text_color="#00ffff", font=("Arial", 14, "bold")).pack(pady=5)
        self.search_local = ctk.CTkEntry(self.left_pane, placeholder_text="🔍 Pesquisar no PC...")
        self.search_local.pack(fill="x", padx=10, pady=5)
        self.search_local.bind("<KeyRelease>", lambda e: self.filtrar_lista("local"))
        
        self.btn_browse_local = ctk.CTkButton(self.left_pane, text="Abrir Pasta", command=self.browse_local)
        self.btn_browse_local.pack(padx=10, pady=5, fill="x")
        
        self.list_local = ctk.CTkTextbox(self.left_pane, font=("Consolas", 12))
        self.list_local.pack(fill="both", expand=True, padx=10, pady=10)

        # Painel Direito (Rocknix)
        self.right_pane = ctk.CTkFrame(self.panes, border_width=2, border_color="#ff00ff")
        self.right_pane.pack(side="right", fill="both", expand=True, padx=5)
        
        ctk.CTkLabel(self.right_pane, text="🎮 ROCKNIX", text_color="#ff00ff", font=("Arial", 14, "bold")).pack(pady=5)
        self.search_remote = ctk.CTkEntry(self.right_pane, placeholder_text="🔍 Pesquisar no Console...")
        self.search_remote.pack(fill="x", padx=10, pady=5)
        self.search_remote.bind("<KeyRelease>", lambda e: self.filtrar_lista("remote"))

        self.storage_label = ctk.CTkLabel(self.right_pane, text="Espaço: --")
        self.storage_label.pack()
        self.storage_bar = ctk.CTkProgressBar(self.right_pane, width=200)
        self.storage_bar.set(0)
        self.storage_bar.pack(pady=5)

        self.list_remote = ctk.CTkTextbox(self.right_pane, font=("Consolas", 12))
        self.list_remote.pack(fill="both", expand=True, padx=10, pady=10)

        # Footer
        self.footer = ctk.CTkFrame(self, height=60, fg_color="transparent")
        self.footer.pack(fill="x", pady=10)

        self.btn_log = ctk.CTkButton(self.footer, text="📋", width=40, command=self.export_log)
        self.btn_log.pack(side="left", padx=10)

        self.btn_health = ctk.CTkButton(self.footer, text="🩺 SAÚDE", fg_color="#2b2b2b", command=self.show_health)
        self.btn_health.pack(side="left", padx=10)

        self.btn_autofix = ctk.CTkButton(self.footer, text="⚡ AUTO-FIX", fg_color="#cc8800", command=self.run_autofix)
        self.btn_autofix.pack(side="left", padx=10)

        self.btn_sync = ctk.CTkButton(self.footer, text="INICIAR SINCRONIZAÇÃO ➔", fg_color="#0088ff", font=("Arial", 14, "bold"))
        self.btn_sync.pack(side="right", padx=20)

    # --- LÓGICA DE FUNCIONAMENTO ---

    def on_device_found(self, name, ip):
        self.dispositivos[name] = ip
        self.device_combo.configure(values=list(self.dispositivos.keys()))
        self.device_combo.set(list(self.dispositivos.keys())[0])

    def connect_to_device(self, name):
        ip = self.dispositivos.get(name)
        self.remote_path = f"\\\\{ip}\\roms" # Padrão SMB Windows
        self.check_storage(self.remote_path)
        self.refresh_list("remote", self.remote_path)

    def check_storage(self, path):
        try:
            total, used, free = shutil.disk_usage(path)
            percent = used / total
            self.storage_label.configure(text=f"{free // (2**30)} GB Livres")
            self.storage_bar.set(percent)
            self.storage_bar.configure(progress_color="#00ff00" if percent < 0.85 else "#ff3333")
        except:
            self.storage_label.configure(text="Erro de Acesso")

    def browse_local(self):
        path = filedialog.askdirectory()
        if path:
            self.local_path = path
            self.refresh_list("local", path)

    def refresh_list(self, lado, path):
        try:
            files = os.listdir(path)
            if lado == "local":
                self.arquivos_locais = files
                self.filtrar_lista("local")
            else:
                self.arquivos_remotos = files
                self.filtrar_lista("remote")
        except: pass

    def filtrar_lista(self, lado):
        if lado == "local":
            termo = self.search_local.get().lower()
            box, dados = self.list_local, self.arquivos_locais
        else:
            termo = self.search_remote.get().lower()
            box, dados = self.list_remote, self.arquivos_remotos
        
        box.delete("1.0", "end")
        for item in dados:
            if termo in item.lower():
                box.insert("end", f"{item}\n")

    def run_autofix(self):
        if not self.local_path: return
        count = 0
        for f in os.listdir(self.local_path):
            new_f = re.sub(r'[^a-zA-Z0-9\._\- ]', '_', f).lower()
            if f != new_f:
                os.rename(os.path.join(self.local_path, f), os.path.join(self.local_path, new_f))
                count += 1
        self.refresh_list("local", self.local_path)
        messagebox.showinfo("Auto-Fix", f"{count} arquivos higienizados!")

    def show_health(self):
        health_win = ctk.CTkToplevel(self)
        health_win.title("Relatório de Saúde")
        health_win.geometry("400x300")
        txt = ctk.CTkTextbox(health_win, fg_color="#000", text_color="#00ff00")
        txt.pack(fill="both", expand=True, padx=10, pady=10)
        
        txt.insert("end", ">>> ANALISANDO BIBLIOTECA...\n")
        # Exemplo de verificação simples
        if not any(".bin" in f.lower() for f in self.arquivos_locais) and self.sys_combo.get() == "psx":
            txt.insert("end", "[ERRO] Arquivos .BIN não detectados para PS1!\n")
        else:
            txt.insert("end", "[OK] Estrutura de arquivos compatível.\n")

    def export_log(self):
        with open("log_rocknix.txt", "w") as f:
            f.write(f"Lista exportada em {datetime.now()}\n" + "\n".join(self.arquivos_remotos))
        messagebox.showinfo("Log", "Arquivo log_rocknix.txt gerado!")

    def open_settings(self):
        sw = ctk.CTkToplevel(self)
        sw.title("Configurações")
        sw.geometry("300x250")
        ctk.CTkSwitch(sw, text="Auto-Rename no Sync", variable=self.cfg_auto_rename).pack(pady=10)
        ctk.CTkSwitch(sw, text="Checar Espaço", variable=self.cfg_check_space).pack(pady=10)
        ctk.CTkSwitch(sw, text="Mostrar Botão Log", variable=self.cfg_show_log, command=self.toggle_log_btn).pack(pady=10)

    def toggle_log_btn(self):
        if self.cfg_show_log.get(): self.btn_log.pack(side="left", padx=10, before=self.btn_health)
        else: self.btn_log.pack_forget()

if __name__ == "__main__":
    app = RocknixGamerManager()
    app.mainloop()
