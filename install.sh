#!/bin/bash

# =================================================================
# App Name: Rocknix Manager Installer
# Description: Installs dependencies in a VENV and creates shortcuts
# =================================================================

# Configuration
APP_NAME="Rocknix Manager"
APP_IMAGE="Rocknix_Manager.AppImage"
VENV_DIR=".venv_rocknix"
LAUNCHER_NAME="rocknix-launcher.sh"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=======================================${NC}"
echo -e "${BLUE}       $APP_NAME - Installer       ${NC}"
echo -e "${BLUE}=======================================${NC}"

# 1. System Dependencies Check
echo -e "\n${YELLOW}[1/5] Checking system dependencies...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python3 is not installed.${NC}"
    exit 1
fi

# 2. Requirements Management
echo -e "${YELLOW}[2/5] Setting up Python dependencies...${NC}"
if [ ! -f "requirements.txt" ]; then
    echo -e "${BLUE}Creating default requirements.txt...${NC}"
    cat <<EOF > requirements.txt
PyQt6
requests
paramiko
EOF
fi

# 3. Virtual Environment Setup (PEP 668 Compliance)
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${BLUE}Creating virtual environment in $VENV_DIR...${NC}"
    python3 -m venv "$VENV_DIR" || { 
        echo -e "${RED}Failed to create VENV. Please run: sudo apt install python3-venv${NC}"
        exit 1 
    }
fi

source "$VENV_DIR/bin/activate"
echo -e "${GREEN}Installing/Updating libraries...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
deactivate

# 4. AppImage Permissions
echo -e "${YELLOW}[3/5] Configuring executable...${NC}"
if [ -f "$APP_IMAGE" ]; then
    chmod +x "$APP_IMAGE"
    echo -e "${GREEN}Execution permission granted to $APP_IMAGE.${NC}"
else
    echo -e "${RED}Warning: $APP_IMAGE not found in current directory.${NC}"
fi

# 5. Create Execution Wrapper
echo -e "${YELLOW}[4/5] Creating launcher script...${NC}"
cat <<EOF > "$LAUNCHER_NAME"
#!/bin/bash
# Get the absolute path of the script directory
DIR="\$(dirname "\$(readlink -f "\$0")")"
# Activate environment and run AppImage
source "\$DIR/$VENV_DIR/bin/activate"
cd "\$DIR"
./$APP_IMAGE "\$@"
EOF
chmod +x "$LAUNCHER_NAME"

# 6. Desktop Integration
echo -e "${YELLOW}[5/5] System integration...${NC}"
read -p "Do you want to create a desktop shortcut? (y/n): " confirm
if [[ "$confirm" =~ ^([yY]|[yY][eE][sS]|[sS])$ ]]; then
    DESKTOP_PATH="$HOME/.local/share/applications/rocknix_manager.desktop"
    FULL_PATH=$(readlink -f "$LAUNCHER_NAME")
    
    # Use generic icon if specific one isn't found
    ICON_PATH="system-run"
    
    cat <<EOF > "$DESKTOP_PATH"
[Desktop Entry]
Version=1.0
Type=Application
Name=$APP_NAME
Comment=Manager for Rocknix ROMs and BIOS
Exec=$FULL_PATH
Icon=$ICON_PATH
Terminal=false
Categories=Utility;Game;
EOF
    echo -e "${GREEN}Shortcut created at: $DESKTOP_PATH${NC}"
fi

echo -e "\n${BLUE}=======================================${NC}"
echo -e "${GREEN}        Installation Completed!        ${NC}"
echo -e "${BLUE}=======================================${NC}"
echo -e "To start the app, run: ${YELLOW}./$LAUNCHER_NAME${NC}"
