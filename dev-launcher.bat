set PYTHONPATH=./;./packages

IF "%1"=="--run-tests" GOTO Test

py -2 app/server.py

:Test
START py -2 app/server.py
pytest tests