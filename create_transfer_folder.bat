@echo off
echo Creating HaazriBook transfer folder...

:: Create main directory
mkdir HaazriBook
cd HaazriBook

:: Create logs directory
mkdir logs

:: Copy essential files
copy ..\app.py .
copy ..\database.py .
copy ..\messaging.py .
copy ..\config.py .
copy ..\staff.db .
copy ..\run_app.bat .
copy ..\run_app_silent.bat .
copy ..\requirements.txt .
copy ..\app_icon.ico .
copy ..\README.md .

:: Create empty logs folder structure
echo. > logs\.gitkeep

echo.
echo Transfer folder created successfully!
echo Location: %CD%
echo.
echo Files included:
echo - app.py
echo - database.py
echo - messaging.py
echo - config.py
echo - staff.db
echo - run_app.bat
echo - run_app_silent.bat
echo - requirements.txt
echo - app_icon.ico
echo - README.md
echo - logs/ directory
echo.
echo You can now transfer the 'HaazriBook' folder to another computer.
pause 