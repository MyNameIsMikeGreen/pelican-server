#!/usr/bin/env bash
echo "Launching Pelican Server..."
VENV_DIR=venv
if [[ ! -d "$VENV_DIR" ]]; then
    echo "$VENV_DIR directory not detected. Creating virtual environment..."
    virtualenv ${VENV_DIR}
fi
source ${VENV_DIR}/bin/activate
pip3 install -r requirements.txt
python3 src/pelican_server.py
deactivate
echo "Pelican Server terminated."
