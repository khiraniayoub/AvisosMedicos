# 🚀 CONFIGURACIÓN MULTI-USUARIO - GUÍA PASO A PASO

## ⚡ INICIO RÁPIDO

### 📍 **PASO 1: Ejecutar Configuración en el PC Servidor**

Este PC actuará como servidor central de la base de datos.

#### Opción A: Automática (Recomendada)
1. Haz **clic derecho** en `EJECUTAR_CONFIGURACION.bat`
2. Selecciona **"Ejecutar como administrador"**
3. Acepta el UAC (Control de Cuentas de Usuario)
4. Sigue las instrucciones en pantalla
5. ✅ ¡Listo!

#### Opción B: Manual
1. Abre PowerShell **como Administrador**
2. Navega a la carpeta del proyecto:
   ```powershell
   cd "C:\Users\Ayoub\Desktop\Proyecto_Avisos"
   ```
3. Ejecuta:
   ```powershell
   .\configurar_multiusuario.ps1
   ```

---

### 📍 **PASO 2: Anotar la IP del Servidor**

Después de ejecutar el script, verás algo como:

```
SERVIDOR CONFIGURADO:
  IP del servidor: 192.168.1.100
  Puerto: 5433
  Base de datos: avisos_db
```

**✏️ ANOTA ESTA IP:** `192.168.1.___`

---

### 📍 **PASO 3: Preparar Ejecutables para Clientes**

#### A. Para el PC SERVIDOR (este PC):
- ✅ Ya está listo
- Usa el ejecutable con el `.env` actual
- Este PC puede ejecutar la aplicación normalmente

#### B. Para OTROS PCs (clientes):

1. **Copia la carpeta completa del ejecutable:**
   ```
   dist\Vithas_Avisos\  (toda la carpeta)
   ```

2. **Edita el archivo `.env` en la carpeta copiada:**
   
   Abre `.env` con Notepad y cambia:
   ```env
   DB_HOST=localhost    ← CAMBIAR ESTO
   ```
   
   Por:
   ```env
   DB_HOST=192.168.1.100    ← IP del servidor (la que anotaste)
   ```

3. **El archivo `.env` completo debe quedar así:**
   ```env
   DB_HOST=192.168.1.100
   DB_PORT=5433
   DB_NAME=avisos_db
   DB_USER=postgres
   DB_PASSWORD=postgres
   ```

4. **Copia toda la carpeta** `Vithas_Avisos` a cada PC cliente

---

### 📍 **PASO 4: Verificar Conexión desde Clientes**

En cada PC cliente:

1. Abre el ejecutable `Vithas_Avisos.exe`
2. Inicia sesión (IISS / IISS2025)
3. Verifica que veas los mismos avisos que en el servidor

**Si funciona:** ✅ Configuración exitosa  
**Si no funciona:** ⚠️ Ver sección de solución de problemas abajo

---

## 🔧 CONFIGURACIÓN DETALLADA

### Lo que hace el script automáticamente:

1. ✅ Detecta la instalación de PostgreSQL
2. ✅ Obtiene la IP del servidor
3. ✅ Crea backup de configuraciones
4. ✅ Modifica `postgresql.conf` para aceptar conexiones de red
5. ✅ Modifica `pg_hba.conf` para permitir autenticación
6. ✅ Configura el firewall de Windows (puerto 5433)
7. ✅ Reinicia el servicio PostgreSQL
8. ✅ Crea archivo `cliente.env` con la configuración

---

## 📋 CHECKLIST DE CONFIGURACIÓN

### En el PC SERVIDOR:
- [ ] PostgreSQL instalado y funcionando
- [ ] Script `configurar_multiusuario.ps1` ejecutado como admin
- [ ] IP del servidor anotada
- [ ] Firewall configurado (puerto 5433 abierto)
- [ ] Servicio PostgreSQL reiniciado

### En cada PC CLIENTE:
- [ ] Carpeta `Vithas_Avisos` completa copiada
- [ ] Archivo `.env` editado con IP del servidor
- [ ] Conexión de red al servidor (mismo WiFi/LAN)
- [ ] Ejecutable probado y funcionando

---

## 🌐 REQUISITOS DE RED

### Todos los PCs deben:
- ✅ Estar en la **misma red local** (WiFi o LAN)
- ✅ Poder hacer **ping** al servidor
- ✅ Tener acceso al **puerto 5433** del servidor

### Verificar conectividad:

En cada PC cliente, abre CMD y ejecuta:
```cmd
ping 192.168.1.100
```

Deberías ver:
```
Respuesta desde 192.168.1.100: bytes=32 tiempo<1ms TTL=128
```

Si ves "Tiempo de espera agotado" → Problema de red/firewall

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### ❌ Error: "No se puede conectar a la base de datos"

**Causa**: El cliente no puede alcanzar el servidor

**Soluciones:**
1. Verifica que el servidor esté encendido
2. Verifica que PostgreSQL esté ejecutándose en el servidor
3. Verifica la IP en el archivo `.env` del cliente
4. Verifica que ambos PCs estén en la misma red
5. Verifica el firewall del servidor (puerto 5433)

**Test de conexión:**
```cmd
# En el PC cliente
telnet 192.168.1.100 5433
```

---

### ❌ Error: "Autenticación fallida"

**Causa**: Password incorrecta

**Solución:**
Edita `.env` en el cliente y verifica:
```env
DB_PASSWORD=postgres    ← Debe ser la password correcta de PostgreSQL
```

---

### ❌ Error: "El script requiere permisos de administrador"

**Solución:**
1. Cierra PowerShell/CMD
2. Haz clic derecho en `EJECUTAR_CONFIGURACION.bat`
3. Selecciona "Ejecutar como administrador"

---

### ❌ Firewall bloquea conexiones

**Solución manual:**

1. Abre **Windows Defender Firewall**
2. Click en **Configuración avanzada**
3. Click en **Reglas de entrada**
4. Click en **Nueva regla...**
5. Selecciona **Puerto** → Siguiente
6. TCP, puerto **5433** → Siguiente
7. **Permitir la conexión** → Siguiente
8. Marca todas las redes → Siguiente
9. Nombre: "PostgreSQL Vithas" → Finalizar

---

### ❌ PostgreSQL no acepta conexiones remotas

**Verificar configuración manual:**

1. Abre `C:\Program Files\PostgreSQL\14\data\postgresql.conf`
2. Busca la línea `listen_addresses`
3. Debe estar así:
   ```
   listen_addresses = '*'
   ```
4. Abre `C:\Program Files\PostgreSQL\14\data\pg_hba.conf`
5. Al final debe tener:
   ```
   host    all    all    0.0.0.0/0    md5
   ```
6. Reinicia PostgreSQL:
   ```powershell
   Restart-Service postgresql-x64-14
   ```

---

## 📊 ARQUITECTURA FINAL

```
┌─────────────────────────────────────────────────┐
│           PC SERVIDOR (192.168.1.100)           │
│                                                 │
│  ┌─────────────────────────────────────┐       │
│  │  PostgreSQL Server                  │       │
│  │  - Puerto: 5433                     │       │
│  │  - Base de datos: avisos_db         │       │
│  │  - 66 avisos almacenados            │       │
│  └─────────────────────────────────────┘       │
│                                                 │
│  ┌─────────────────────────────────────┐       │
│  │  Vithas_Avisos.exe                  │       │
│  │  .env: DB_HOST=localhost            │       │
│  └─────────────────────────────────────┘       │
└─────────────────────────────────────────────────┘
                      │
                      │ Red Local (WiFi/LAN)
                      │
        ┌─────────────┼─────────────┐
        │             │             │
┌───────▼──────┐ ┌───▼────────┐ ┌──▼─────────┐
│   PC 1       │ │   PC 2     │ │   PC 3     │
│              │ │            │ │            │
│ Vithas.exe   │ │ Vithas.exe │ │ Vithas.exe │
│ .env:        │ │ .env:      │ │ .env:      │
│ DB_HOST=     │ │ DB_HOST=   │ │ DB_HOST=   │
│ 192.168.1.100│ │ 192.168... │ │ 192.168... │
└──────────────┘ └────────────┘ └────────────┘

Todos los PCs → Misma base de datos → Datos sincronizados ✅
```

---

## ✅ VERIFICACIÓN FINAL

### Test de Multi-Usuario:

1. **PC Servidor**: Crea un aviso nuevo
2. **PC Cliente 1**: Abre la aplicación → Debe ver el aviso nuevo
3. **PC Cliente 2**: Edita el aviso
4. **PC Servidor**: Debe ver la edición
5. **PC Cliente 3**: Elimina el aviso
6. **Todos los PCs**: El aviso debe desaparecer

**Si todo funciona:** 🎉 ¡Sistema multi-usuario configurado!

---

## 📞 SOPORTE

### Comandos útiles:

**Ver estado de PostgreSQL:**
```powershell
Get-Service postgresql*
```

**Reiniciar PostgreSQL:**
```powershell
Restart-Service postgresql-x64-14
```

**Ver IP del servidor:**
```powershell
ipconfig
```

**Test de conexión desde cliente:**
```cmd
ping 192.168.1.100
telnet 192.168.1.100 5433
```

---

## 🎯 RESUMEN

1. ✅ Ejecuta `EJECUTAR_CONFIGURACION.bat` como admin en el servidor
2. ✅ Anota la IP del servidor
3. ✅ Copia el ejecutable a otros PCs
4. ✅ Edita `.env` en cada cliente con la IP del servidor
5. ✅ ¡Todos los PCs comparten la misma base de datos!

---

**¡Configuración completada!** 🚀

Todos los ordenadores ahora guardarán y compartirán datos en tiempo real.
