# Script de configuración automática de PostgreSQL
# Ejecutar DESPUÉS de instalar PostgreSQL

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CONFIGURACIÓN DE POSTGRESQL" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si PostgreSQL está instalado
Write-Host "1. Verificando instalación de PostgreSQL..." -ForegroundColor Yellow
try {
    $version = psql --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ PostgreSQL encontrado: $version" -ForegroundColor Green
    } else {
        throw "PostgreSQL no encontrado"
    }
} catch {
    Write-Host "   ✗ PostgreSQL no está instalado o no está en el PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor:" -ForegroundColor Yellow
    Write-Host "1. Descarga PostgreSQL desde: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads" -ForegroundColor White
    Write-Host "2. Instala PostgreSQL" -ForegroundColor White
    Write-Host "3. Agrega PostgreSQL al PATH (C:\Program Files\PostgreSQL\16\bin)" -ForegroundColor White
    Write-Host "4. Reinicia PowerShell y ejecuta este script nuevamente" -ForegroundColor White
    Write-Host ""
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host ""

# Solicitar credenciales
Write-Host "2. Configuración de credenciales" -ForegroundColor Yellow
Write-Host ""
Write-Host "   Ingresa la contraseña que configuraste para el usuario 'postgres'" -ForegroundColor White
Write-Host "   (La que elegiste durante la instalación de PostgreSQL)" -ForegroundColor Gray
Write-Host ""
$password = Read-Host "   Contraseña de PostgreSQL" -AsSecureString
$passwordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($password)
)

Write-Host ""

# Verificar conexión
Write-Host "3. Verificando conexión a PostgreSQL..." -ForegroundColor Yellow
$env:PGPASSWORD = $passwordPlain
$testConnection = psql -U postgres -c "SELECT version();" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ Conexión exitosa" -ForegroundColor Green
} else {
    Write-Host "   ✗ Error de conexión. Verifica que:" -ForegroundColor Red
    Write-Host "     - La contraseña sea correcta" -ForegroundColor White
    Write-Host "     - El servicio PostgreSQL esté corriendo" -ForegroundColor White
    Write-Host ""
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host ""

# Crear base de datos
Write-Host "4. Creando base de datos 'avisos_db'..." -ForegroundColor Yellow
$createDb = psql -U postgres -c "CREATE DATABASE avisos_db;" 2>&1
if ($LASTEXITCODE -eq 0 -or $createDb -like "*already exists*") {
    Write-Host "   ✓ Base de datos lista" -ForegroundColor Green
} else {
    Write-Host "   ⚠ Advertencia: $createDb" -ForegroundColor Yellow
}

Write-Host ""

# Ejecutar script de configuración
Write-Host "5. Creando tablas..." -ForegroundColor Yellow
if (Test-Path "setup_database.sql") {
    $setupDb = psql -U postgres -d avisos_db -f setup_database.sql 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ Tablas creadas exitosamente" -ForegroundColor Green
    } else {
        Write-Host "   ⚠ Advertencia: $setupDb" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ⚠ Archivo setup_database.sql no encontrado" -ForegroundColor Yellow
}

Write-Host ""

# Actualizar archivo .env
Write-Host "6. Configurando archivo .env..." -ForegroundColor Yellow
$envContent = @"
# PostgreSQL Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=avisos_db
DB_USER=postgres
DB_PASSWORD=$passwordPlain

# Telegram Bot Configuration (opcional)
TELEGRAM_BOT_TOKEN=TU_TOKEN_AQUI
"@

$envContent | Out-File -FilePath ".env" -Encoding UTF8
Write-Host "   ✓ Archivo .env actualizado" -ForegroundColor Green

Write-Host ""

# Migrar datos
Write-Host "7. ¿Deseas migrar los datos de CSV a PostgreSQL? (S/N)" -ForegroundColor Yellow
$migrate = Read-Host "   Respuesta"
if ($migrate -eq "S" -or $migrate -eq "s") {
    Write-Host "   Migrando datos..." -ForegroundColor White
    python src/migrate_csv_to_db.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ Datos migrados exitosamente" -ForegroundColor Green
    } else {
        Write-Host "   ⚠ Error durante la migración" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ⊘ Migración omitida" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ✓ CONFIGURACIÓN COMPLETADA" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ahora puedes ejecutar tu aplicación:" -ForegroundColor White
Write-Host "  python main.py" -ForegroundColor Cyan
Write-Host ""

# Limpiar variable de entorno
$env:PGPASSWORD = $null

Read-Host "Presiona Enter para salir"
