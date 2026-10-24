@echo off
setlocal
where py >nul 2>nul
if errorlevel 1 (
  where python >nul 2>nul
  if errorlevel 1 (
    echo Python 3.11 or newer is required. Install Python and try again.
    pause
    exit /b 1
  )
  python "%~dp0launch_powerbi.py"
) else (
  py -3 "%~dp0launch_powerbi.py"
)
if errorlevel 1 (
  pause
  exit /b 1
)
endlocal
