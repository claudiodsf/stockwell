@echo off
REM Test Stockwell on Windows using pytest
REM Allows for a temporary test failure by repeating the test 5 times
REM (c) 2024-2025 Claudio Satriano <satriano@ipgp.fr>
set /a n=0
:loop
pytest --pyargs stockwell && exit /b 0
set /a n+=1
if %n% gtr 5 goto :end
goto :loop
:end
