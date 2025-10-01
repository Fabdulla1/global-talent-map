@echo off
echo 🚀 Global Talent Map - Data Processing
echo =====================================
echo.

echo Checking Python environment...
if not exist ".venv" (
    echo Creating Python virtual environment...
    python -m venv .venv
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Installing/updating dependencies...
pip install pandas openpyxl --quiet

echo.
echo 📊 Processing scholar data...
python process_data.py

echo.
echo ✨ Data processing completed!
echo The website has been updated with the latest data.
echo.
pause