@echo off
REM Build a wheel on Windows.
REM Uses `wheel_repair.py` to include fftw3.dll into the wheel
REM (c) 2021 Claudio Satriano

set OLDPWD=%cd%
cd ..
python setup.py bdist_wheel
cd %OLDPWD%
for %%i in (..\dist\*.whl) do (
    python .\wheel_repair.py ^
        -d %userprofile%\anaconda3\Library\bin -w ../wheels %%i
)
rmdir ..\dist /q /s