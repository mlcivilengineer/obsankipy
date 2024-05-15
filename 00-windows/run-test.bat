rem
rem Create test decks
rem

pushd ..

python ./src/obsankipy.py ./examples/vault/.obsankipy/config.yaml
if ERRORLEVEL 1 ( echo ERROR & exit /b 1 )

pause

exit /b 0
