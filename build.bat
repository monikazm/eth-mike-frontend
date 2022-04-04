@echo off
REM -- Create Python virtual environment if it does not exist
IF NOT EXIST venv\ (
    python -m venv venv
)

@echo on
REM -- Activate virtual environment and ensure Python package dependencies are installed in it
call venv\Scripts\activate.bat
pip install -r requirements.txt

REM -- Build self-contained exe file using PyInstaller
python -OO -m PyInstaller --clean --noupx --exclude-module FixTk --exclude-module tcl --exclude-module tk --exclude-module _tkinter --exclude-module tkinter --exclude-module Tkinter --onefile main.py

REM -- Rename the created exe and move it to root directory
copy dist\main.exe Simulator.exe
rmdir /S /Q dist
