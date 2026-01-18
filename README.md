# 🎮 Rocknix ROM Manager

Um gerenciador de ROMs com interface visual "Gamer" desenvolvido especialmente para usuários do ROCKNIX. 

### ✨ Funcionalidades
- 🚀 **Auto-Discovery:** Encontra seu console na rede automaticamente.
- 🩺 **Health Report:** Verifica a saúde dos nomes dos arquivos e BIOS.
- ⚡ **Auto-Fix:** Corrige nomes de arquivos incompatíveis com Linux instantaneamente.
- 📊 **Storage Monitor:** Mostra o espaço livre no SD Card em tempo real.

### 🚀 Como Rodar no Ubuntu
```bash
# Clone o repositório
git clone [https://github.com/xtrempkch-droid/rocknix_manager.git](https://github.com/xtrempkch-droid/rocknix_manager.git)
cd rocknix_manager

# Crie o ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Rode o app
python3 main.py
