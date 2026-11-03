@echo off
setlocal
cd /d "%~dp0"
if errorlevel 1 (
    echo ERROR: Cannot open the project directory.
    exit /b 1
)

if not exist "requirements.txt" (
    echo ERROR: requirements.txt was not found.
    exit /b 1
)

if exist ".venv\Scripts\python.exe" goto check_venv
if exist ".venv" (
    echo ERROR: .venv exists but its Python executable is missing. Check the environment before retrying.
    exit /b 1
)

py -3 -c "import sys; sys.exit(sys.version_info < (3, 11))"
if errorlevel 1 (
    echo ERROR: Python 3.11 or newer and the Windows Python launcher are required.
    exit /b 1
)
py -3 -m venv .venv
if errorlevel 1 (
    echo ERROR: Could not create .venv.
    exit /b 1
)

:check_venv
".venv\Scripts\python.exe" -c "import sys; sys.exit(sys.version_info < (3, 11))"
if errorlevel 1 (
    echo ERROR: The .venv Python is unavailable or older than Python 3.11.
    exit /b 1
)
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Dependency installation failed. Check the pip output above.
    exit /b 1
)
echo Setup complete. Run RUN_LOCAL.cmd to start the app.
exit /b 0
