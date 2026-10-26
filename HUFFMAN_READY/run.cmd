@echo off
setlocal
cd /d "%~dp0"
if not exist "backend\.venv\Scripts\python.exe" goto setup
if not exist "core\huffman_core.exe" goto setup
echo Mo Chrome hoac Edge: http://127.0.0.1:5000
echo Giu nguyen cua so nay trong khi su dung.
"backend\.venv\Scripts\python.exe" backend\app.py
exit /b
:setup
echo Hay chay setup.cmd truoc. Xem README.md.
exit /b 1
