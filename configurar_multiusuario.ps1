# Script para configurar PostgreSQL para acceso multi-usuario en red local
# EJECUTAR EN EL PC QUE ACTUARÁ COMO SERVIDOR

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CONFIGURACION MULTI-USUARIO" -ForegroundColor Cyan
Write-Host "  PostgreSQL - Vithas Avisos" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si se está ejecutando como administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: Este script debe ejecutarse como Administrador" -ForegroundColor Red
    Write-Host "Haz clic derecho y selecciona 'Ejecutar como administrador'" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "1. Detectando instalacion de PostgreSQL..." -ForegroundColor Yellow

# Buscar instalación de PostgreSQL
$pgPaths = @(
    "C:\Program Files\PostgreSQL\14\data",
    "C:\Program Files\PostgreSQL\15\data",
    "C:\Program Files\PostgreSQL\16\data",
    "C:\PostgreSQL\14\data",
    "C:\PostgreSQL\15\data"
)

$pgDataPath = $null
foreach ($path in $pgPaths) {
    if (Test-Path $path) {
        $pgDataPath = $path
        break
    }
}

if (-not $pgDataPath) {
    Write-Host "ERROR: No se encontro PostgreSQL instalado" -ForegroundColor Red
    Write-Host "Instala PostgreSQL primero usando setup_postgresql.ps1" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "   PostgreSQL encontrado en: $pgDataPath" -ForegroundColor Green
Write-Host ""

# Obtener IP local
Write-Host "2. Detectando IP del servidor..." -ForegroundColor Yellow
$ipAddress = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*" -and $_.IPAddress -notlike "169.254.*"} | Select-Object -First 1).IPAddress

if ($ipAddress) {
    Write-Host "   IP del servidor: $ipAddress" -ForegroundColor Green
} else {
    Write-Host "   ADVERTENCIA: No se pudo detectar IP automaticamente" -ForegroundColor Yellow
    $ipAddress = Read-Host "   Ingresa la IP manualmente"
}
Write-Host ""

# Backup de archivos de configuración
Write-Host "3. Creando backup de configuracion..." -ForegroundColor Yellow
$backupDate = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item "$pgDataPath\postgresql.conf" "$pgDataPath\postgresql.conf.backup_$backupDate" -ErrorAction SilentlyContinue
Copy-Item "$pgDataPath\pg_hba.conf" "$pgDataPath\pg_hba.conf.backup_$backupDate" -ErrorAction SilentlyContinue
Write-Host "   Backup creado" -ForegroundColor Green
Write-Host ""

# Modificar postgresql.conf
Write-Host "4. Configurando postgresql.conf..." -ForegroundColor Yellow
$postgresqlConf = Get-Content "$pgDataPath\postgresql.conf"
$newConf = @()
$listenAddressFound = $false

foreach ($line in $postgresqlConf) {
    if ($line -match "^\s*#?\s*listen_addresses\s*=") {
        $newConf += "listen_addresses = '*'		# Modificado para multi-usuario"
        $listenAddressFound = $true
    } else {
        $newConf += $line
    }
}

if (-not $listenAddressFound) {
    $newConf += "listen_addresses = '*'		# Añadido para multi-usuario"
}

$newConf | Set-Content "$pgDataPath\postgresql.conf"
Write-Host "   postgresql.conf actualizado" -ForegroundColor Green
Write-Host ""

# Modificar pg_hba.conf
Write-Host "5. Configurando pg_hba.conf..." -ForegroundColor Yellow
$pgHbaConf = Get-Content "$pgDataPath\pg_hba.conf"
$newHba = @()
$ruleAdded = $false

foreach ($line in $pgHbaConf) {
    $newHba += $line
}

# Añadir regla para red local
$newHba += ""
$newHba += "# Configuracion multi-usuario - Vithas Avisos"
$newHba += "host    all             all             0.0.0.0/0               md5"

$newHba | Set-Content "$pgDataPath\pg_hba.conf"
Write-Host "   pg_hba.conf actualizado" -ForegroundColor Green
Write-Host ""

# Configurar firewall
Write-Host "6. Configurando firewall de Windows..." -ForegroundColor Yellow
try {
    # Eliminar regla existente si existe
    Remove-NetFirewallRule -DisplayName "PostgreSQL Vithas" -ErrorAction SilentlyContinue
    
    # Crear nueva regla
    New-NetFirewallRule -DisplayName "PostgreSQL Vithas" `
                        -Direction Inbound `
                        -LocalPort 5433 `
                        -Protocol TCP `
                        -Action Allow `
                        -Profile Any | Out-Null
    
    Write-Host "   Regla de firewall creada (Puerto 5433)" -ForegroundColor Green
} catch {
    Write-Host "   ADVERTENCIA: No se pudo configurar firewall automaticamente" -ForegroundColor Yellow
    Write-Host "   Abre el puerto 5433 manualmente en el firewall" -ForegroundColor Yellow
}
Write-Host ""

# Reiniciar servicio PostgreSQL
Write-Host "7. Reiniciando servicio PostgreSQL..." -ForegroundColor Yellow
$services = Get-Service | Where-Object {$_.Name -like "postgresql*"}

if ($services) {
    foreach ($service in $services) {
        try {
            Restart-Service $service.Name -Force
            Write-Host "   Servicio $($service.Name) reiniciado" -ForegroundColor Green
        } catch {
            Write-Host "   ERROR: No se pudo reiniciar $($service.Name)" -ForegroundColor Red
            Write-Host "   Reinicia el servicio manualmente" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "   ADVERTENCIA: No se encontro servicio PostgreSQL" -ForegroundColor Yellow
    Write-Host "   Reinicia PostgreSQL manualmente" -ForegroundColor Yellow
}
Write-Host ""

# Crear archivo .env para clientes
Write-Host "8. Creando archivo .env para clientes..." -ForegroundColor Yellow
$clientEnv = @"
# Configuracion para CLIENTES (otros PCs)
# Copia este archivo junto con el ejecutable

DB_HOST=$ipAddress
DB_PORT=5433
DB_NAME=avisos_db
DB_USER=postgres
DB_PASSWORD=postgres

# IMPORTANTE: Cambia DB_PASSWORD por tu password real de PostgreSQL
"@

$clientEnv | Set-Content "cliente.env"
Write-Host "   Archivo 'cliente.env' creado" -ForegroundColor Green
Write-Host ""

# Resumen final
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CONFIGURACION COMPLETADA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "SERVIDOR CONFIGURADO:" -ForegroundColor Green
Write-Host "  IP del servidor: $ipAddress" -ForegroundColor White
Write-Host "  Puerto: 5433" -ForegroundColor White
Write-Host "  Base de datos: avisos_db" -ForegroundColor White
Write-Host ""
Write-Host "PROXIMOS PASOS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. En ESTE PC (servidor):" -ForegroundColor Cyan
Write-Host "   - Mantener PostgreSQL ejecutandose" -ForegroundColor White
Write-Host "   - Usar el .env actual (localhost)" -ForegroundColor White
Write-Host ""
Write-Host "2. En OTROS PCs (clientes):" -ForegroundColor Cyan
Write-Host "   - Copiar el ejecutable completo" -ForegroundColor White
Write-Host "   - Reemplazar .env con 'cliente.env'" -ForegroundColor White
Write-Host "   - Editar cliente.env y cambiar DB_PASSWORD" -ForegroundColor White
Write-Host "   - Ejecutar Vithas_Avisos.exe" -ForegroundColor White
Write-Host ""
Write-Host "3. Verificar conexion desde cliente:" -ForegroundColor Cyan
Write-Host "   psql -h $ipAddress -p 5433 -U postgres -d avisos_db" -ForegroundColor White
Write-Host ""
Write-Host "ARCHIVOS CREADOS:" -ForegroundColor Yellow
Write-Host "  - cliente.env (configuracion para otros PCs)" -ForegroundColor White
Write-Host "  - postgresql.conf.backup_$backupDate" -ForegroundColor White
Write-Host "  - pg_hba.conf.backup_$backupDate" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

pause
