@echo off
setlocal
set BUILD_DIR=build

rem Обновление из Git (если есть upstream)
git rev-parse --abbrev-ref --symbolic-full-name @{u} >nul 2>nul
if %errorlevel%==0 (
    git pull
)

if not exist %BUILD_DIR% mkdir %BUILD_DIR%
cd /d %BUILD_DIR%

cmake -G "MinGW Makefiles" ..
cmake --build .

endlocal
