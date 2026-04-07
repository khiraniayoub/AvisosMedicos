@echo off
echo ========================================
echo   CONFIGURACION MULTI-USUARIO
echo   Ejecutando con permisos elevados...
echo ========================================
echo.

:: Verificar permisos de administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Ejecutando con permisos de administrador...
    powershell -ExecutionPolicy Bypass -File "%~dp0configurar_multiusuario.ps1"
) else (
    echo Solicitando permisos de administrador...
    powershell -Command "Start-Process cmd -ArgumentList '/c cd /d %~dp0 && powershell -ExecutionPolicy Bypass -File configurar_multiusuario.ps1 && pause' -Verb RunAs"
)
