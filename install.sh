# shellcheck disable=SC2162
read -p "Enter installation path: " PyFS_Path

BOLD="\033[1m"
RESET="\033[0m"
WHITE="\033[37m"
GREEN="\033[32m"
RED="\033[31m"

if command -v uv >/dev/null 2>&1; then
    echo "uv is installed"
else
    echo -e "${RED}${BOLD}uv is not installed${RESET}"
    echo "Installing with pip"
    python -m pip install uv
    echo -e "${GREEN}${BOLD}Installed${RESET}, please restart your terminal and rerun this script"
    exit 0
fi

# shellcheck disable=SC2164
cd "$PyFS_Path"
git clone https://github.com/G1aD05/PyFleet-Scratch.git
# shellcheck disable=SC2164
cd PyFleet-Scratch

uv sync

echo -e "Install for PyFleet-Scratch has finished, you can run it by using ${BOLD}${WHITE}uv run cli.py${RESET}"
