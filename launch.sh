#!/usr/bin/env bash
echo "Launching Pelican Server..."
ORIGINAL_DIRECTORY="`pwd`"
LOCAL_DIRECTORY="`dirname ${0}`"
cd ${LOCAL_DIRECTORY}
VENV_DIR=venv
if [[ ! -d "$VENV_DIR" ]]; then
    echo "$VENV_DIR directory not detected. Creating virtual environment..."
    virtualenv ${VENV_DIR}
fi
source ${VENV_DIR}/bin/activate
pip3 install -r requirements.txt
python3 src/pelicanserver.py
deactivate
cd ${ORIGINAL_DIRECTORY}
echo "Pelican Server terminated."
