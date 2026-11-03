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
".venv\Scripts\python.exe" -m pytest -q
if errorlevel 1 (
    echo ERROR: Tests failed. Check the pytest output above.
    exit /b 1
)
echo Tests passed.
exit /b 0
