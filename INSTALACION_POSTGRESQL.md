# Guía de Instalación y Configuración de PostgreSQL

## 📥 Paso 1: Descargar PostgreSQL

1. Ve a: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
2. Descarga **PostgreSQL 16.x** para Windows
3. Ejecuta el instalador descargado

## 🔧 Paso 2: Instalación

Durante la instalación, configura lo siguiente:

1. **Directorio de instalación**: Deja el valor por defecto
   - `C:\Program Files\PostgreSQL\16`

2. **Componentes**: Selecciona TODOS
   - ✅ PostgreSQL Server
   - ✅ pgAdmin 4
   - ✅ Stack Builder
   - ✅ Command Line Tools

3. **Directorio de datos**: Deja el valor por defecto
   - `C:\Program Files\PostgreSQL\16\data`

4. **⚠️ IMPORTANTE - Contraseña del superusuario**:
   - Usuario: `postgres`
   - Contraseña: Elige una y **RECUÉRDALA** (ejemplo: `postgres123`)
   - **Anota esta contraseña, la necesitarás después**

5. **Puerto**: Deja el valor por defecto
   - Puerto: `5432`

6. **Locale**: Selecciona `Spanish, Spain` o `Default locale`

7. Haz clic en "Next" hasta que comience la instalación

## ✅ Paso 3: Verificar la Instalación

Después de instalar, abre una **nueva ventana de PowerShell** y ejecuta:

```powershell
psql --version
```

Deberías ver algo como: `psql (PostgreSQL) 16.x`

## 🗄️ Paso 4: Crear la Base de Datos

### Opción A: Usando pgAdmin (Interfaz Gráfica)

1. Abre **pgAdmin 4** desde el menú de inicio
2. Conéctate al servidor local (usa la contraseña que configuraste)
3. Click derecho en "Databases" → "Create" → "Database"
4. Nombre: `avisos_db`
5. Click en "Save"

### Opción B: Usando la línea de comandos

Abre PowerShell y ejecuta:

```powershell
# Conectar a PostgreSQL
psql -U postgres

# Cuando te pida la contraseña, ingresa la que configuraste
# Luego ejecuta:
CREATE DATABASE avisos_db;
\q
```

## 📝 Paso 5: Ejecutar el Script de Configuración

En PowerShell, navega a la carpeta del proyecto y ejecuta:

```powershell
cd C:\Users\Ayoub\Desktop\Proyecto_Avisos
psql -U postgres -d avisos_db -f setup_database.sql
```

## 🔐 Paso 6: Configurar el archivo .env

Edita el archivo `.env` en la carpeta del proyecto con tus credenciales:

```env
# PostgreSQL Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=avisos_db
DB_USER=postgres
DB_PASSWORD=TU_CONTRASEÑA_AQUI
```

**Reemplaza `TU_CONTRASEÑA_AQUI` con la contraseña que configuraste en el Paso 2**

## 📊 Paso 7: Migrar Datos de CSV a PostgreSQL

Ejecuta el script de migración:

```powershell
python src/migrate_csv_to_db.py
```

## 🚀 Paso 8: ¡Listo!

Ahora ejecuta tu aplicación:

```powershell
python main.py
```

La aplicación debería conectarse a PostgreSQL sin errores.

---

## ❓ Solución de Problemas

### Error: "psql no se reconoce como comando"

Necesitas agregar PostgreSQL al PATH:

1. Busca "Variables de entorno" en Windows
2. Edita la variable `Path`
3. Agrega: `C:\Program Files\PostgreSQL\16\bin`
4. Reinicia PowerShell

### Error: "connection refused"

1. Verifica que el servicio de PostgreSQL esté corriendo:
   - Abre "Servicios" en Windows
   - Busca "postgresql-x64-16"
   - Debe estar "En ejecución"

### Error: "authentication failed"

- Verifica que la contraseña en `.env` sea correcta
- Verifica que el usuario sea `postgres`

---

## 📞 ¿Necesitas ayuda?

Si tienes algún problema durante la instalación, avísame en qué paso estás y te ayudaré.
