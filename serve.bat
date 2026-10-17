@echo off
cd /d "%~dp0"
echo kdocs preview server. First build takes about 90 seconds.
echo URL: http://127.0.0.1:8123/kdocs/
echo Press Ctrl+C to stop.
".venv\Scripts\mkdocs.exe" serve -a 127.0.0.1:8123 --open
pause
