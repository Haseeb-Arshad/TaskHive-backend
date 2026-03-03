@echo off
cd /d F:\TaskHive\taskhive-api
.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
