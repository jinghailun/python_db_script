@echo off
setlocal enabledelayedexpansion

REM =======================================================================
REM === Find Python installation, then execute python script ===
REM =======================================================================

REM === Step 1: Try to find real Python installation under LocalAppData ===
set "PYTHON_PATH="
for %%P in (
    "%LocalAppData%\Microsoft\WindowsApps\python3.12.exe"
    "%LocalAppData%\Microsoft\WindowsApps\python3.exe"
    "%LocalAppData%\Microsoft\WindowsApps\python3*"
    "%LocalAppData%\Microsoft\WindowsApps\python.exe"
    "%LocalAppData%\Programs\Python\Python3*"
    "%ProgramFiles%\Python3*"
    "%ProgramFiles(x86)%\Python3*"
) do (
    if exist "%%~P" (
        set "PYTHON_PATH=%%~P"
        goto :FOUND
    )
)


REM === Step 2: Try using `where python` (could be stub in WindowsApps) ===
for /f "delims=" %%i in ('where python 2^>nul') do (
    set "PYTHON_PATH=%%i"
    goto :FOUND
)


:NOT_FOUND
echo Python executable not found. Please ensure Python is installed.
pause
exit /b 1

:FOUND
REM try to run
for /f "delims=" %%v in ('"%PYTHON_PATH%" --version 2^>nul') do (
    set "PYTHON_OK=1"
)

if defined PYTHON_OK (
    echo ------------------------------------------------------------------------
    "%PYTHON_PATH%" --version
) else (
    echo %PYTHON_PATH% is not a valid Python executable.
    PAUSE
    exit /b 1
)
echo.
echo LocalAppData: %LocalAppData%
echo Python found at: %PYTHON_PATH%
"%PYTHON_PATH%" --version
echo --------------------------------------------------------------------------

REM
SET SCRIPT_PATH=%~dp0main.py

REM

rem echo %~dp0/db_backup/back_up_dev_db.py
rem echo Python : "%PYTHON_PATH%"
echo Script : "%SCRIPT_PATH%"

echo.
echo.
echo.
REM

@REM SET VAN_SQL_PATH="C:\Work\db_bak\backup_db\backup_salesErp_van_20250415_171755.sql"
SET VAN_SQL_PATH="C:\Work\db_bak\backup_db\backup_salesErp_van_20250416_132838.sql"
SET TOR_SQL_PATH="C:\Work\db_bak\backup_db\backup_salesErp_tor_20250416_132655.sql"
SET EDM_SQL_PATH="C:\Work\db_bak\backup_db\backup_salesErp_edm_20250416_133039.sql"
SET CAL_SQL_PATH="C:\Work\db_bak\backup_db\backup_salesErp_cal_20250416_133250.sql"

"%PYTHON_PATH%" "%SCRIPT_PATH%" --database "salesErp_van" --backup_file "%VAN_SQL_PATH%" --sql_script "C:\Work\db_bak\modify_user_local&van.sql"
"%PYTHON_PATH%" "%SCRIPT_PATH%" --database "salesErp_tor" --backup_file "%TOR_SQL_PATH%" --sql_script "C:\Work\db_bak\modify_user_tor.sql"
"%PYTHON_PATH%" "%SCRIPT_PATH%" --database "salesErp_edm" --backup_file "%EDM_SQL_PATH%" --sql_script "C:\Work\db_bak\modify_user_edm.sql"
"%PYTHON_PATH%" "%SCRIPT_PATH%" --database "salesErp_cal" --backup_file "%CAL_SQL_PATH%" --sql_script "C:\Work\db_bak\modify_user_cal.sql"

REM 
PAUSE
