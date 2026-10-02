#!/bin/bash
echo "Setting up Ad Studio Environment..."

python3 -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt

echo -e "\nEnvironment setup complete!"
echo "To start, run: source venv/bin/activate"
