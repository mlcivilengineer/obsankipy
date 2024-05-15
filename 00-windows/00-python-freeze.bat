@echo off


echo.
echo.
echo %~n0: Freezing ...
echo.
echo.

pushd ..

pip freeze > %~dp0\requirements.txt
if ERRORLEVEL 1 ( echo %~n0: ERROR pip freeze & goto err_handler )

type %~dp0\requirements.txt


echo.
echo.
echo %~n0: Freezing ALL ...
echo.
echo.

pip freeze --all > %~dp0\requirements-all.txt
if ERRORLEVEL 1 ( echo %~n0: ERROR pip freeze all & goto err_handler )

popd

echo.
echo OK
echo.

:exit_handler
pause
exit /b 0
:err_handler
pause
exit /b 1

