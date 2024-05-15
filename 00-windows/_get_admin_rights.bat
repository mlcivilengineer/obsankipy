@echo off
rem --------------------------------------------------------------------------------
rem Pruefrt auf Adminrechte, falls nicht vorhanden: Besorgt sie!
rem --------------------------------------------------------------------------------


>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"

if '%errorlevel%' NEQ '0' (

                REM Get ADMIN Privileges
                echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
                echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
                "%temp%\getadmin.vbs"
                del "%temp%\getadmin.vbs"
                
                echo %~dpn0: Now running with ADMIN Privileges                
                exit /b 0

) else (
                REM Got ADMIN Privileges
                pushd "%cd%"
                cd /d "%~dp0"
                @echo on
                
                echo %~dpn0: You already HAD ADMIN Privileges                
                exit /b 0
)

