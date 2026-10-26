@echo off
setlocal
cd /d "%~dp0"
python --version
if errorlevel 1 goto fail
if not exist "backend\.venv\Scripts\python.exe" python -m venv backend\.venv
if errorlevel 1 goto fail
"backend\.venv\Scripts\python.exe" -m pip install -r backend\requirements.txt
if errorlevel 1 goto fail
"backend\.venv\Scripts\python.exe" build_core.py
if errorlevel 1 goto fail
"backend\.venv\Scripts\python.exe" tests\test_system.py
if errorlevel 1 goto fail
echo.
echo Setup thanh cong. Chay run.cmd va mo http://127.0.0.1:5000
exit /b 0
:fail
echo.
echo Setup chua hoan tat. Doc loi ben tren va README.md.
exit /b 1
