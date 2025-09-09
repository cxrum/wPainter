@echo off
SETLOCAL

REM -----------------------------
REM Check if virtual environment exists
REM -----------------------------
IF NOT EXIST ".venv" (
    echo Creating virtual environment...
    python -m venv venv
    call .venv\Scripts\activate
    echo Installing dependencies...
    pip install --upgrade pip
    pip install -r requirements.txt
) ELSE (
    call .venv\Scripts\activate
)

REM -----------------------------
REM Info for the user
REM -----------------------------
echo.
echo =========================================
echo Your program is starting...
echo WARNING: Your mouse will be captured while drawing.
echo Close this window to stop the program.
echo =========================================
echo.

REM -----------------------------
REM Run your main Python script
REM -----------------------------
python main.py

REM -----------------------------
REM Clean up / deactivate environment
REM -----------------------------
deactivate
ENDLOCAL
