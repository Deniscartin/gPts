@echo off
echo 🚀 Building Gasolio Tracker for Windows...

REM Create and activate virtual environment
echo 📦 Creating virtual environment...
python -m venv venv
call venv\Scripts\activate

REM Install requirements
echo 📥 Installing dependencies...
pip install -r requirements.txt
pip install pyinstaller

REM Build executable
echo 🔨 Building executable...
pyinstaller --clean gasolio.spec

REM Create distribution zip
echo 📦 Creating distribution package...
cd dist
powershell Compress-Archive -Path "Gasolio Tracker" -DestinationPath "Gasolio_Tracker_Windows.zip" -Force
cd ..

echo ✅ Build complete!
echo.
echo 📁 The executable is in the dist folder
echo 📦 A zip package has been created at dist/Gasolio_Tracker_Windows.zip
echo.
echo 🎯 To run the application:
echo    1. Extract Gasolio_Tracker_Windows.zip
echo    2. Run "Gasolio Tracker.exe"
echo.
pause 