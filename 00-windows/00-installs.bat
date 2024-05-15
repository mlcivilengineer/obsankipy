@echo off

rem Installing into Global Store -> Run as Admin
call %~dp0\_get_admin_rights.bat
if ERRORLEVEL 1 ( echo ERROR _get_admin_rights & goto err_handler )

@echo off

echo CD is: %CD%



rem set UPGRADE_FLAGS=--upgrade
set UPGRADE_FLAGS=


echo Use this with care -- Installing into Global Store!
echo UPGRADE_FLAGS: %UPGRADE_FLAGS%
echo Hit CTRL-C to cancel ...
pause


python.exe -m pip install --upgrade pip
if ERRORLEVEL 1 (echo error pip upgrade & goto err_handler )


pip install annotated-types %UPGRADE_FLAGS%
if ERRORLEVEL 1 (echo error install & goto err_handler )

pip install certifi %UPGRADE_FLAGS%
if ERRORLEVEL 1 (echo error install & goto err_handler )

pip install charset-normalizer %UPGRADE_FLAGS%
if ERRORLEVEL 1 (echo error install & goto err_handler )

pip install idna %UPGRADE_FLAGS%
if ERRORLEVEL 1 (echo error install & goto err_handler )

pip install markdown %UPGRADE_FLAGS%
if ERRORLEVEL 1 (echo error install & goto err_handler )

pip install pydantic-core %UPGRADE_FLAGS%
if ERRORLEVEL 1 (echo error install & goto err_handler )

pip install pydantic %UPGRADE_FLAGS%
if ERRORLEVEL 1 (echo error install & goto err_handler )

pip install pygments %UPGRADE_FLAGS%
if ERRORLEVEL 1 (echo error install & goto err_handler )

pip install python-frontmatter %UPGRADE_FLAGS%
if ERRORLEVEL 1 (echo error install & goto err_handler )

pip install pyyaml %UPGRADE_FLAGS%
if ERRORLEVEL 1 (echo error install & goto err_handler )

pip install requests %UPGRADE_FLAGS%
if ERRORLEVEL 1 (echo error install & goto err_handler )

pip install typing-extensions %UPGRADE_FLAGS%
if ERRORLEVEL 1 (echo error install & goto err_handler )

pip install urllib3 %UPGRADE_FLAGS%
if ERRORLEVEL 1 (echo error install & goto err_handler )


echo.
echo.
echo All Installations succeeded successfully!
echo.
echo.


rem FREEZE
call %~dp0\00-python-freeze.bat
if ERRORLEVEL 1 goto err_handler


:exit_handler
pause
exit /b 0
:err_handler
pause
exit /b 1

