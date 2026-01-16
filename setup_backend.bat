@echo off
setlocal

set PYTHON_EXE="C:\Program Files\Python312\python.exe"

if not exist %PYTHON_EXE% (
    echo [ERROR] Python not found at %PYTHON_EXE%
    exit /b 1
)

%PYTHON_EXE% --version

cd backend

if not exist "venv" (
    echo [INFO] Creating venv...
    %PYTHON_EXE% -m venv venv
)

echo [INFO] Activating venv...
call venv\Scripts\activate.bat

echo [INFO] Installing requirements...
pip install -r requirements.txt

echo [INFO] Starting Server...
python app.py
