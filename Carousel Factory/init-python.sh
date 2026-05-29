#!/bin/bash
if ! command -v pip3 &> /dev/null; then
    echo "Installing pip..."
    curl -sSL https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py --user --break-system-packages
    rm get-pip.py
fi
echo "Installing pip requirements..."
python3 -m pip install -r requirements.txt --user --break-system-packages
