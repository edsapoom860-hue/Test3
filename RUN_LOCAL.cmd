@echo off
setlocal
cd /d "%~dp0"
if errorlevel 1 (
    echo ERROR: Cannot open the project directory.
    exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
    echo ERROR: .venv Python not found. Run SETUP.cmd first.
    exit /b 1
)
if not exist "app.py" (
    echo ERROR: app.py was not found.
    exit /b 1
)
echo Starting UBE Safety Talk at http://127.0.0.1:8501
".venv\Scripts\python.exe" -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
if errorlevel 1 (
    echo ERROR: Streamlit failed to start or stopped with an error. Check the output above and whether port 8501 is in use.
    exit /b 1
)
exit /b 0
