@echo off
echo ========================================
echo   EJECUTABLE DE UN SOLO ARCHIVO
echo   (Mas facil de distribuir)
echo ========================================
echo.

echo NOTA: Este ejecutable sera un solo archivo .exe
echo pero tardara mas en iniciar (10-30 segundos)
echo.
echo Si prefieres inicio rapido, usa build_portable.bat
echo.
pause

echo [1/3] Limpiando builds anteriores...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

echo.
echo [2/3] Construyendo ejecutable de un solo archivo...
echo (Esto puede tardar 5-10 minutos)
echo.

pyinstaller --clean --noconfirm ^
    --name "Vithas_Avisos_Portable" ^
    --windowed ^
    --onefile ^
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
echo Ubicacion: dist\Vithas_Avisos_Portable.exe
echo.
echo ========================================
echo   CONSTRUCCION COMPLETADA
echo ========================================
echo.
echo VENTAJAS:
echo  + Un solo archivo .exe (facil de distribuir)
echo  + No necesita carpeta de dependencias
echo.
echo DESVENTAJAS:
echo  - Tarda mas en iniciar (10-30 segundos)
echo  - Archivo mas grande (~200-400 MB)
echo.
pause
