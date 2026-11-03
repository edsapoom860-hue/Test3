@echo off
setlocal
cd /d "%~dp0"
if errorlevel 1 (
    echo ERROR: Cannot open project directory.
    exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Run SETUP.cmd first.
    exit /b 1
)
if "%~1"=="" (
    echo Usage: NETWORK_DEMO.cmd ^<approved-private-IPv4-address^>
    exit /b 1
)
set "NETWORK_BIND=%~1"
".venv\Scripts\python.exe" -c "import ipaddress,os,sys; a=ipaddress.ip_address(os.environ['NETWORK_BIND']); sys.exit(not (a.version == 4 and any(a in ipaddress.ip_network(n) for n in ('10.0.0.0/8','172.16.0.0/12','192.168.0.0/16'))))"
if errorlevel 1 (
    echo ERROR: Supply an authorized private IPv4 address: 10.x, 172.16-31.x or 192.168.x.
    exit /b 1
)
set "NETWORK_READONLY=1"
set "PYTHONPATH=%~dp0"
echo NETWORK DEMO: fictional data only, read-only, no authentication.
echo Listening at http://%NETWORK_BIND%:8502 - stop with Ctrl+C.
".venv\Scripts\python.exe" -m streamlit run network_demo\app.py --server.address "%NETWORK_BIND%" --server.port 8502 --browser.gatherUsageStats false
if errorlevel 1 (
    echo ERROR: Network demo failed. Check the address, port and Streamlit output above.
    exit /b 1
)
exit /b 0
