# 🖥️ MULTI-USUARIO: COMPARTIR DATOS ENTRE EJECUTABLES

## ❓ PREGUNTA: ¿Los datos se comparten entre varios ordenadores?

**RESPUESTA CORTA**: Depende de la configuración.

---

## 📊 ESCENARIO 1: EJECUTABLES INDEPENDIENTES (ACTUAL)

### ❌ **NO se comparten los datos**

Si cada ordenador tiene su propia copia del ejecutable:

```
PC 1 → Ejecutable + avisos.csv (local)
PC 2 → Ejecutable + avisos.csv (local)
PC 3 → Ejecutable + avisos.csv (local)
PC 4 → Ejecutable + avisos.csv (local)
```

### ¿Qué pasa?
- Cada PC guarda datos en su **propio archivo CSV local**
- Los datos **NO se sincronizan** entre PCs
- Cada PC tiene su **propia base de datos independiente**

### Ejemplo:
1. PC1 crea aviso "Paciente A" → Solo visible en PC1
2. PC2 crea aviso "Paciente B" → Solo visible en PC2
3. PC3 abre el programa → Solo ve sus propios avisos
4. **Resultado**: Cada PC tiene datos diferentes ❌

---

## ✅ ESCENARIO 2: BASE DE DATOS CENTRALIZADA (RECOMENDADO)

### ✅ **SÍ se comparten los datos**

Si todos los PCs se conectan a la **misma base de datos PostgreSQL**:

```
                    ┌─────────────────────┐
                    │  SERVIDOR CENTRAL   │
                    │  PostgreSQL DB      │
                    │  (avisos_db)        │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
    ┌───▼───┐             ┌───▼───┐             ┌───▼───┐
    │  PC1  │             │  PC2  │             │  PC3  │
    │  .exe │             │  .exe │             │  .exe │
    └───────┘             └───────┘             └───────┘
```

### ¿Qué pasa?
- Todos los PCs se conectan al **mismo servidor PostgreSQL**
- Los datos se guardan en **una única base de datos central**
- **Todos ven los mismos datos en tiempo real** ✅
- Cambios de un PC son visibles en todos los demás

### Ejemplo:
1. PC1 crea aviso "Paciente A" → Visible en TODOS los PCs
2. PC2 edita el aviso → Cambio visible en TODOS
3. PC3 elimina un aviso → Se elimina para TODOS
4. PC4 abre el programa → Ve TODOS los avisos
5. **Resultado**: Base de datos compartida ✅

---

## 🔧 CÓMO CONFIGURAR MULTI-USUARIO

### OPCIÓN A: Servidor PostgreSQL en Red Local

#### 1️⃣ **Servidor Central** (Un PC actúa como servidor)

Instala PostgreSQL en un PC que esté siempre encendido:

```powershell
# En el PC servidor
# Editar postgresql.conf
listen_addresses = '*'  # Escuchar en todas las interfaces

# Editar pg_hba.conf
host    avisos_db    postgres    192.168.1.0/24    md5
```

#### 2️⃣ **Clientes** (Otros PCs)

En cada PC cliente, configura el archivo `.env`:

```env
DB_HOST=192.168.1.100    # IP del servidor PostgreSQL
DB_PORT=5433
DB_NAME=avisos_db
DB_USER=postgres
DB_PASSWORD=tu_password
```

#### 3️⃣ **Distribuir Ejecutable**

Copia el ejecutable con el `.env` configurado a cada PC.

---

### OPCIÓN B: Servidor PostgreSQL en la Nube

#### Proveedores Recomendados:

1. **AWS RDS** (Amazon)
2. **Azure Database** (Microsoft)
3. **Google Cloud SQL**
4. **Heroku Postgres** (Gratis hasta cierto límite)
5. **ElephantSQL** (PostgreSQL como servicio)

#### Configuración:

```env
# En TODOS los PCs
DB_HOST=tu-servidor.postgres.database.azure.com
DB_PORT=5432
DB_NAME=avisos_db
DB_USER=postgres@servidor
DB_PASSWORD=tu_password_seguro
```

---

### OPCIÓN C: Carpeta Compartida en Red (Híbrido)

Si no quieres servidor PostgreSQL, usa CSV en carpeta compartida:

#### 1️⃣ **Crear carpeta compartida en red**

```
\\SERVIDOR\Vithas_Datos\
  ├── avisos.csv
  ├── hoteles.csv
  └── medicos.csv
```

#### 2️⃣ **Modificar el código** para usar ruta de red

```python
# En main.py, cambiar:
CSV_FILE = r"\\SERVIDOR\Vithas_Datos\avisos.csv"
```

⚠️ **ADVERTENCIA**: CSV compartido tiene limitaciones:
- ❌ Lento con muchos usuarios simultáneos
- ❌ Riesgo de corrupción de datos
- ❌ Sin control de concurrencia
- ✅ Fácil de configurar
- ✅ No requiere servidor de base de datos

---

## 🎯 RECOMENDACIÓN SEGÚN CASO DE USO

### 📌 **1-2 Usuarios** → CSV en carpeta compartida
- Configuración simple
- Sin servidor necesario
- Suficiente para uso ligero

### 📌 **3-10 Usuarios** → PostgreSQL en PC local como servidor
- Mejor rendimiento
- Datos centralizados
- Control de concurrencia
- Requiere un PC siempre encendido

### 📌 **10+ Usuarios** → PostgreSQL en la nube
- Máximo rendimiento
- Acceso desde cualquier lugar
- Alta disponibilidad
- Backups automáticos
- Costo mensual (~$10-50/mes)

---

## 🛠️ CONFIGURACIÓN ACTUAL DE TU PROYECTO

### Estado Actual:
```
✅ PostgreSQL instalado localmente (localhost:5433)
✅ Base de datos: avisos_db con 66 registros
❌ Configurado para UN SOLO PC (localhost)
```

### Para Multi-Usuario:
```
🔧 Necesitas configurar PostgreSQL para red
🔧 O usar servidor PostgreSQL en la nube
🔧 O cambiar a CSV compartido (no recomendado)
```

---

## 📋 PASOS PARA HABILITAR MULTI-USUARIO

### MÉTODO 1: PostgreSQL en Red Local (Recomendado)

#### Paso 1: Configurar Servidor PostgreSQL
```powershell
# En el PC servidor (donde está PostgreSQL)
cd "C:\Program Files\PostgreSQL\14\data"

# Editar postgresql.conf
notepad postgresql.conf
# Cambiar: listen_addresses = '*'

# Editar pg_hba.conf
notepad pg_hba.conf
# Añadir: host all all 0.0.0.0/0 md5

# Reiniciar PostgreSQL
Restart-Service postgresql-x64-14
```

#### Paso 2: Abrir Puerto en Firewall
```powershell
New-NetFirewallRule -DisplayName "PostgreSQL" -Direction Inbound -LocalPort 5433 -Protocol TCP -Action Allow
```

#### Paso 3: Configurar Clientes
En cada PC cliente, editar `.env`:
```env
DB_HOST=192.168.1.X    # IP del servidor
DB_PORT=5433
DB_NAME=avisos_db
DB_USER=postgres
DB_PASSWORD=tu_password
```

#### Paso 4: Distribuir Ejecutable
Copiar carpeta `dist\Vithas_Avisos\` con el `.env` configurado.

---

### MÉTODO 2: CSV Compartido (Rápido pero limitado)

#### Paso 1: Crear carpeta compartida
```powershell
# En el servidor de archivos
New-Item -Path "C:\Vithas_Compartido" -ItemType Directory
New-SmbShare -Name "Vithas" -Path "C:\Vithas_Compartido" -FullAccess "Everyone"
```

#### Paso 2: Modificar código
Necesitarías modificar `main.py` para usar rutas UNC:
```python
CSV_FILE = r"\\SERVIDOR\Vithas\avisos.csv"
```

#### Paso 3: Recompilar ejecutable
```bash
build_portable.bat
```

---

## ⚠️ IMPORTANTE: SINCRONIZACIÓN DE DATOS

### Con PostgreSQL Central:
✅ **Sincronización automática** en tiempo real
✅ Todos ven los mismos datos
✅ Sin conflictos

### Con CSV Local (actual):
❌ **NO hay sincronización**
❌ Cada PC tiene sus propios datos
❌ Datos se pierden al cerrar

### Con CSV Compartido:
⚠️ **Sincronización manual** (al abrir/cerrar)
⚠️ Riesgo de conflictos si 2 usuarios editan a la vez
⚠️ Puede corromperse el archivo

---

## 🎯 RESUMEN EJECUTIVO

### ¿Los datos se guardan entre ejecuciones?

| Escenario | ¿Se guardan? | ¿Se comparten? |
|-----------|--------------|----------------|
| **Ejecutable local con CSV local** | ✅ Sí (en ese PC) | ❌ No |
| **Ejecutable local con PostgreSQL local** | ✅ Sí (en ese PC) | ❌ No |
| **Ejecutable con PostgreSQL en red** | ✅ Sí | ✅ Sí |
| **Ejecutable con CSV compartido** | ✅ Sí | ⚠️ Limitado |

### Tu Configuración Actual:
- **PostgreSQL local** (localhost:5433)
- **Datos**: Se guardan en ese PC
- **Multi-usuario**: ❌ NO configurado

### Para Habilitar Multi-Usuario:
1. Configurar PostgreSQL para red (Método 1)
2. O usar PostgreSQL en la nube
3. Actualizar `.env` en cada PC con IP del servidor
4. Distribuir ejecutable con `.env` configurado

---

## 📞 ¿Necesitas Ayuda?

¿Quieres que configure el sistema multi-usuario?

Dime qué opción prefieres:
1. **PostgreSQL en red local** (gratis, requiere PC servidor)
2. **PostgreSQL en la nube** (pago, acceso desde cualquier lugar)
3. **CSV compartido** (simple pero limitado)

Y te ayudo a configurarlo paso a paso.
