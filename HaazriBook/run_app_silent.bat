@echo off
:: Hide the command window
if not DEFINED IS_MINIMIZED set IS_MINIMIZED=1 && start "" /min "%~dpnx0" %* && exit

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed! Please install Python 3.8 or higher.
    pause
    exit
)

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    python -m venv venv
)

:: Activate virtual environment
call venv\Scripts\activate

:: Install required packages
pip install streamlit pandas plotly streamlit-option-menu

:: Start the application and open browser
start http://localhost:8501
streamlit run app.py --server.headless true --server.runOnSave false

:: Exit the script
exit 