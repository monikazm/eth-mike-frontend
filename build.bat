@echo off
IF NOT EXIST venv\ (
@echo on
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
)

@echo on
call venv\Scripts\activate.bat
pyinstaller --onefile mike_simulator\main.py
copy dist\main.exe Simulator.exe
rmdir /S /Q dist
rmdir /S /Q mike_simulator\__pycache__
rmdir /S /Q mike_simulator\assessment_modes\__pycache__
rmdir /S /Q mike_simulator\input_backends\__pycache__
