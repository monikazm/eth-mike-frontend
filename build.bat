@echo off
IF NOT EXIST venv\ (
@echo on
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
)

@echo on
call venv\Scripts\activate.bat
pyinstaller --onefile main.py
copy dist\main.exe Simulator.exe
rmdir /S /Q dist
rmdir /S /Q __pycache__
rmdir /S /Q assessment_modes\__pycache__