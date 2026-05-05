@echo off
setlocal

set SCRIPT_DIR=%~dp0
set PROJECT_DIR=%SCRIPT_DIR%..

docker stop pm-app 2>nul
docker rm pm-app 2>nul

docker build -t pm-app "%PROJECT_DIR%"
docker run -d --name pm-app -p 8000:8000 ^
  --env-file "%PROJECT_DIR%\.env" ^
  -v "%PROJECT_DIR%\data:/app/data" ^
  pm-app

echo App running at http://localhost:8000
