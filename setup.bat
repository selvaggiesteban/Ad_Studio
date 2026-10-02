@echo off
echo Setting up Ad Studio Environment...

python -m venv venv
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Environment setup complete!
echo To start, run: call venv\Scripts\activate
echo.
pause
