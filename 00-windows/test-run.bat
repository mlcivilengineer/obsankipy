@echo off

rem
rem Create test decks
rem

pushd ..

echo Creating test decks ...

python ./src/obsankipy.py ./examples/vault/.obsankipy/config.yaml
if ERRORLEVEL 1 ( echo ERROR & exit /b 1 )

echo DONE!

pause

exit /b 0
