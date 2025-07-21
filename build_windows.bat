@echo off
echo 🚀 Building Gasolio Tracker for Windows...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python non trovato! Installa Python 3.8+ e riprova.
    pause
    exit /b 1
)

REM Create and activate virtual environment
echo 📦 Creating virtual environment...
if exist venv (
    echo 🔄 Removing existing virtual environment...
    rmdir /s /q venv
)
python -m venv venv
if errorlevel 1 (
    echo ❌ Errore nella creazione dell'ambiente virtuale!
    pause
    exit /b 1
)

call venv\Scripts\activate
if errorlevel 1 (
    echo ❌ Errore nell'attivazione dell'ambiente virtuale!
    pause
    exit /b 1
)

REM Upgrade pip
echo 📦 Updating pip...
python -m pip install --upgrade pip

REM Install requirements
echo 📥 Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Errore nell'installazione delle dipendenze!
    echo ℹ️  Controlla requirements.txt e la connessione internet
    pause
    exit /b 1
)

REM Clean previous builds
echo 🧹 Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build executable
echo 🔨 Building executable...
pyinstaller --clean gasolio.spec
if errorlevel 1 (
    echo ❌ Errore nella build dell'eseguibile!
    echo ℹ️  Controlla gasolio.spec e i log di PyInstaller
    pause
    exit /b 1
)

REM Check if executable was created
if not exist "dist\Gasolio_Tracker.exe" (
    echo ❌ Eseguibile non trovato in dist\Gasolio_Tracker.exe
    echo ℹ️  Controlla i log di PyInstaller per errori
    pause
    exit /b 1
)

REM Create distribution folder
echo 📦 Creating distribution package...
if exist "Gasolio_Tracker_Windows" rmdir /s /q "Gasolio_Tracker_Windows"
mkdir "Gasolio_Tracker_Windows"

REM Copy executable and required files
echo 📋 Copying files...
copy "dist\Gasolio_Tracker.exe" "Gasolio_Tracker_Windows\"
xcopy /E /I "dist\platts" "Gasolio_Tracker_Windows\platts" >nul 2>&1

REM Create README for distribution
echo 📄 Creating README...
(
echo Gasolio Tracker - Windows Executable
echo ===================================
echo.
echo Per avviare l'applicazione:
echo 1. Esegui "Gasolio_Tracker.exe"
echo 2. Attendi che si apra automaticamente nel browser
echo 3. Se non si apre automaticamente, vai a http://127.0.0.1:5001
echo.
echo Note:
echo - L'applicazione richiede una connessione internet
echo - I dati Firebase sono necessari per l'autenticazione
echo - Per chiudere l'applicazione, chiudi la finestra del terminale
echo.
echo Supporto: Controlla i log nella finestra del terminale per eventuali errori
) > "Gasolio_Tracker_Windows\README.txt"

REM Create zip package
cd Gasolio_Tracker_Windows
powershell Compress-Archive -Path * -DestinationPath "..\Gasolio_Tracker_Windows.zip" -Force
cd ..

echo.
echo ✅ Build completed successfully!
echo.
echo 📁 File creati:
echo    - Eseguibile: Gasolio_Tracker_Windows\Gasolio_Tracker.exe
echo    - Pacchetto ZIP: Gasolio_Tracker_Windows.zip
echo.
echo 🎯 Per testare l'applicazione:
echo    1. Vai nella cartella Gasolio_Tracker_Windows
echo    2. Esegui Gasolio_Tracker.exe
echo.
echo 📦 Per distribuire l'applicazione:
echo    - Condividi il file Gasolio_Tracker_Windows.zip
echo.
pause 
