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
rmdir /S /Q build
rmdir /S /Q __pycache__
del main.spec