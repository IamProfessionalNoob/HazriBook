@echo off
echo Setting up HaazriBook Application...

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed! Please install Python 3.8 or higher.
    pause
    exit
)

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
call venv\Scripts\activate

:: Install required packages
echo Installing required packages...
pip install streamlit pandas plotly streamlit-option-menu

:: Run the application
echo Starting HaazriBook...
echo The application will be available at http://localhost:8501
streamlit run app.py

:: Keep the window open if there's an error
pause 