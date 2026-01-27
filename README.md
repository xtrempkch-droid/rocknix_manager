Rocknix Manager 🎮

[Português] | [English]

O Rocknix Manager é uma ferramenta para facilitar a gestão de jogos, bios e configurações para o sistema ROCKNIX.

🇧🇷 Português

Instalação Rápida

Copie e cole o comando abaixo no seu terminal para instalar automaticamente:

curl -sSL [https://raw.githubusercontent.com/xtrempkch-droid/rocknix_manager/main/install.sh](https://raw.githubusercontent.com/xtrempkch-droid/rocknix_manager/main/install.sh) | bash


Requisitos

Python 3.x

Git

Como usar

Após a instalação, entre na pasta e execute:

cd ~/rocknix_manager
source venv/bin/activate
python3 main.py


🇺🇸 English

Quick Installation

Copy and paste the command below into your terminal to install automatically:

curl -sSL [https://raw.githubusercontent.com/xtrempkch-droid/rocknix_manager/main/install.sh](https://raw.githubusercontent.com/xtrempkch-droid/rocknix_manager/main/install.sh) | bash


Requirements

Python 3.x

Git

How to use

After installation, enter the folder and run:

cd ~/rocknix_manager
source venv/bin/activate
python3 main.py


![alt text](https://github.com/xtrempkch-droid/rocknix_manager/blob/main/ui.png)


Rocknix Manager V7.2 - Recursive Fix Edition 🚀

O Rocknix Manager é uma ferramenta completa para gestão de ROMs e BIOS para dispositivos que utilizam o sistema operativo Rocknix. Esta versão foca-se na restauração de funcionalidades críticas de busca e identificação automática de ficheiros.

✨ Novidades da V7.2

Scan Recursivo (Restauração): Agora o gestor utiliza busca profunda (rglob), encontrando jogos em subpastas, independentemente da organização da tua biblioteca.

Lista de Extensões Expandida: Suporte para mais de 40 formatos, incluindo:

CDs: .cdi, .gdi, .chd, .iso, .cue, .pbp.

Modernos: .rvz (Wii/GameCube), .wbfs, .cso.

Retro: .a26, .d64, .adf, .ipf, .nes, .sfc, etc.

DNA Pro (Deep Inspection): Identificação de sistemas através do cabeçalho binário (Header) para evitar que ficheiros .chd ou .iso sejam enviados para a pasta errada.

🛠️ Funcionalidades Principais

🎮 Gestão de ROMs

Identificação Automática: O motor DNA lê os primeiros bytes do ficheiro para saber se é uma ROM de Sega Saturn, PlayStation ou Dreamcast.

Compressão Automática: Opção para comprimir ficheiros em .zip em tempo real para sistemas que suportam este formato (NES, SNES, Megadrive, etc.).

Envio Multi-Modo: - Samba/Network: Montagem automática via GIO/GVFS.

SFTP/SSH: Envio direto via protocolo seguro (requer paramiko).

Local: Gestão direta para cartões SD ou pens USB montadas no PC.

🧬 Gestão de BIOS

Auditoria Local: Verifica se o teu pack de BIOS tem os hashes MD5 correctos antes de fazeres o upload.

Auditoria Remota: Liga-se ao teu Rocknix via SSH e verifica quais as BIOS que faltam ou que estão corrompidas no dispositivo.

Deploy Inteligente: Envia apenas as BIOS válidas para a pasta correcta (/storage/roms/bios).

🚀 Como Utilizar

Instala as dependências:

pip install PyQt6 paramiko

Executa o Script:

python rocknix_manager_v7_2_recursive.py

Modo Rede: - Clica em "Sincronizar Rede". O programa tentará encontrar o teu dispositivo automaticamente pelo nome ROCKNIX.local.

Adicionar Jogos:

Clica em "Adicionar ROMs" e seleciona a pasta raiz onde guardas os teus jogos. O scan recursivo tratará do resto.

Enviar:

Define o sistema de destino (se o DNA não o fizer por ti) e clica em "Enviar ROMs".

📋 Requisitos

Python 3.8+

PyQt6 (Interface Gráfica)

Paramiko (Opcional, para funções SSH/SFTP)

GIO/GVFS (Recomendado em Linux para montagem automática de pastas de rede)

Desenvolvido para a comunidade Rocknix. Mantém os teus jogos organizados e as tuas BIOS validadas!
