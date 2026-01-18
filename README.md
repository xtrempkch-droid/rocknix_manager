# 🎮 Rocknix ROM Manager

![License](https://img.shields.io/github/license/xtrempkch-droid/rocknix_manager?style=for-the-badge&color=ff00ff)
![Python](https://img.shields.io/badge/Python-3.10+-00ffff?style=for-the-badge&logo=python)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-white?style=for-the-badge)

O **Rocknix ROM Manager** é um gerenciador de arquivos de alto desempenho com interface visual inspirada na estética Gamer (Ciano & Magenta). Ele foi projetado para facilitar a vida de quem utiliza dispositivos com o sistema **ROCKNIX**, permitindo organizar bibliotecas de jogos localmente e via rede.



---

## ✨ Funcionalidades

* 🛰️ **Auto-Discovery:** Detecta automaticamente dispositivos Rocknix na sua rede local (ZeroConf).
* ⚡ **Auto-Fix:** Higieniza nomes de arquivos instantaneamente (remove caracteres especiais e corrige extensões).
* 🩺 **Health Report:** Diagnóstico pré-transferência para checar BIOS ausentes e erros de compatibilidade.
* 📊 **Storage Monitor:** Barra de espaço em tempo real para evitar que o cartão SD fique cheio.
* 🔍 **Busca Instantânea:** Encontre qualquer jogo em milissegundos, mesmo em coleções gigantes.
* 📂 **Dual-Pane UI:** Interface de painel duplo para arrastar e soltar arquivos entre o PC e o Console.

---

## 🚀 Como Instalar (Ubuntu 25.10+)

Devido às novas políticas do Ubuntu para ambientes Python, recomenda-se o uso de um ambiente virtual (`venv`):

```bash
# Clone o repositório
git clone [https://github.com/xtrempkch-droid/rocknix_manager.git](https://github.com/xtrempkch-droid/rocknix_manager.git)
cd rocknix_manager

# Instale as dependências do sistema necessárias para a interface
sudo apt update
sudo apt install python3-venv python3-tk -y

# Crie e ative o ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instale as dependências do projeto
pip install -r requirements.txt

# Execute o aplicativo
python3 main.py




