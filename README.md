Markdown

# ROCKNIX Manager - v0.1 Start Edition

Ferramenta automatizada para gerir, otimizar e enviar ROMs para o console ROCKNIX via rede (SMB) ou Cartão SD local.

## ✨ Funcionalidades
- **Identificação Inteligente:** Usa a base de dados Libretro (No-Intro) para renomear ficheiros.
- **Compressão On-the-fly:** Converte automaticamente ISO/CUE/GDI para **CHD** localmente antes de enviar.
- **Suporte Nativo:** Dreamcast, PSP, PS1, Saturn e sistemas clássicos (NES, SNES, MD).
- **Lógica de Rede Start Edition:** Detecção automática de pontos de montagem `games-external` e `games-internal`.

## 🛠️ Instalação
No terminal, dentro da pasta do projeto:

chmod +x install.sh
./install.sh


🚀 Como usar

    Ligue o seu console e conecte-o à mesma rede Wi-Fi.

    Anote o IP do console.

    Abra o gestor: ./rocknix_manager.py.

    Faça o Scan da sua pasta de ROMs no PC.

    Digite o IP e clique em Iniciar.

📋 Requisitos

    Python 3.x

    chdman e 7z instalados no sistema (para compressão).
