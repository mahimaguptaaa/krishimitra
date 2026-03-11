@echo off
start cmd /k "python -m uvicorn app:app --reload"
start cmd /k "python -m http.server 5500"