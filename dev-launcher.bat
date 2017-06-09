echo off
set PYTHONPATH=./;./packages

IF "%1"=="--run-tests" GOTO Test

py -2 app/server.py

:Test
echo Running tests...
START py -2 app/server.py
echo Starting server instance...
ping 127.0.0.1 -n 3 > nul
pytest tests