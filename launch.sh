#!/usr/bin/env bash


echo "Performing environment setup..."
ORIGINAL_DIRECTORY="`pwd`"
LOCAL_DIRECTORY="`dirname ${0}`"
cd ${LOCAL_DIRECTORY}
LOG_FILE=./pelicanServerLog.log
if [[ ! -f "$LOG_FILE" ]]; then
    touch ${LOG_FILE}
fi
chmod -R 757 ${LOG_FILE}
VENV_DIR=venv
if [[ ! -d "$VENV_DIR" ]]; then
    echo "$VENV_DIR directory not detected. Creating virtual environment..."
    virtualenv ${VENV_DIR}
fi
source ${VENV_DIR}/bin/activate
pip3 install -r requirements.txt


echo "Running tests..."
if pytest ; then
    echo "Tests completed successfully."
else
    echo "Tests failed. Launch aborted."
    exit 1
fi


echo "Building frontend..."
npm install
npm run build


echo "Launching Pelican Server..."
python3 src/pelicanserver.py


echo "Performing environment teardown..."
deactivate
cd ${ORIGINAL_DIRECTORY}
echo "Pelican Server terminated."
