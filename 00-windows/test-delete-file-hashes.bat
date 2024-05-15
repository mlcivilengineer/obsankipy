@echo off

rem
rem Delete file hashes from vault
rem

set HASHES_PATH=examples\vault\.obsankipy\.vault_file_hashes.json

pushd ..

echo.
echo Deleting file hashes:
echo %HASHES_PATH%
echo.
echo.
pause


if EXIST %HASHES_PATH% (
    del %HASHES_PATH%
    if ERRORLEVEL 1 ( echo ERROR del & pause & exit /b 1 )
)

popd

echo DONE!

pause
exit /b 0
