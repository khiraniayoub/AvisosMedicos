@echo off
echo ========================================
echo   CONSTRUYENDO EJECUTABLE PORTABLE
echo   Vithas Avisos - Sistema de Gestion
echo ========================================
echo.

echo [1/3] Limpiando builds anteriores...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

echo.
echo [2/3] Construyendo ejecutable con PyInstaller...
echo (Esto puede tardar varios minutos)
echo.

pyinstaller --clean --noconfirm ^
    --name "Vithas_Avisos" ^
    --windowed ^
    --onedir ^
    --add-data "logo.png;." ^
    --add-data "vithas_bg.png;." ^
    --add-data "avisos.csv;." ^
    --add-data "hoteles.csv;." ^
    --add-data "medicos.csv;." ^
    --add-data "hoteles_coords.json;." ^
    --add-data "teams_config.json;." ^
    --add-data ".env;." ^
    --add-data "src;src" ^
    --hidden-import "PyQt6.QtCore" ^
    --hidden-import "PyQt6.QtGui" ^
    --hidden-import "PyQt6.QtWidgets" ^
    --hidden-import "PyQt6.QtWebEngineWidgets" ^
    --hidden-import "matplotlib.backends.backend_qt5agg" ^
    --hidden-import "folium.plugins" ^
    --hidden-import "psycopg2" ^
    --hidden-import "src.database" ^
    --collect-all "folium" ^
    --collect-all "matplotlib" ^
    main.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: La construccion fallo.
    pause
    exit /b 1
)

echo.
echo [3/3] Ejecutable creado exitosamente!
echo.
echo Ubicacion: dist\Vithas_Avisos\
echo Archivo ejecutable: Vithas_Avisos.exe
echo.
echo ========================================
echo   CONSTRUCCION COMPLETADA
echo ========================================
echo.
echo Puedes copiar toda la carpeta "dist\Vithas_Avisos" a cualquier PC
echo y ejecutar Vithas_Avisos.exe sin instalar nada.
echo.
pause
