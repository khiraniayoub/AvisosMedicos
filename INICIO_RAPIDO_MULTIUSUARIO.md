# ✅ CONFIGURACIÓN MULTI-USUARIO - INICIO

## 🎯 OBJETIVO
Configurar 4 ordenadores para que compartan la misma base de datos de avisos.

---

## 📋 PASOS RÁPIDOS

### ⚡ PASO 1: Configurar el Servidor (ESTE PC)

1. Haz **clic derecho** en: `EJECUTAR_CONFIGURACION.bat`
2. Selecciona: **"Ejecutar como administrador"**
3. Acepta el UAC cuando aparezca
4. **ANOTA LA IP** que aparece al final (ejemplo: 192.168.1.100)

**Tiempo estimado:** 2 minutos

---

### ⚡ PASO 2: Verificar Configuración del Servidor

1. Ejecuta: `python test_multiusuario.py`
2. Verifica que diga: "CONFIGURACION OPERATIVA"
3. Anota la IP que muestra

**Tiempo estimado:** 30 segundos

---

### ⚡ PASO 3: Preparar Ejecutables para Otros PCs

Para cada uno de los otros 3 PCs:

1. **Copia** toda la carpeta: `dist\Vithas_Avisos\`
2. **Pega** en un USB o carpeta compartida
3. **Abre** el archivo `.env` con Notepad
4. **Cambia** esta línea:
   ```
   DB_HOST=localhost
   ```
   Por (usa la IP que anotaste):
   ```
   DB_HOST=192.168.1.100
   ```
5. **Guarda** el archivo `.env`
6. **Copia** la carpeta al otro PC

**Tiempo estimado:** 5 minutos por PC

---

### ⚡ PASO 4: Verificar en Otros PCs

En cada PC cliente:

1. Abre la carpeta `Vithas_Avisos`
2. Ejecuta: `python test_multiusuario.py`
3. Debe decir: "Este PC es un CLIENTE conectado a: 192.168.1.X"
4. Si funciona, ejecuta: `Vithas_Avisos.exe`

**Tiempo estimado:** 2 minutos por PC

---

## ✅ VERIFICACIÓN FINAL

### Test de Sincronización:

1. **PC 1** (servidor): Crea un aviso nuevo
2. **PC 2**: Abre la app → Debe ver el aviso
3. **PC 3**: Edita el aviso
4. **PC 4**: Debe ver la edición
5. **PC 1**: Elimina el aviso
6. **Todos**: El aviso desaparece

**Si todo funciona:** 🎉 ¡Configuración exitosa!

---

## 📁 ARCHIVOS IMPORTANTES

| Archivo | Descripción | Cuándo usar |
|---------|-------------|-------------|
| `EJECUTAR_CONFIGURACION.bat` | Configura el servidor | Una vez, en el PC servidor |
| `test_multiusuario.py` | Verifica conexión | En servidor y clientes |
| `GUIA_CONFIGURACION_PASO_A_PASO.md` | Guía detallada | Si hay problemas |
| `MULTI_USUARIO_GUIA.md` | Explicación completa | Para entender el sistema |

---

## 🐛 PROBLEMAS COMUNES

### ❌ "No se puede conectar"
→ Verifica que el servidor esté encendido  
→ Verifica la IP en `.env`  
→ Verifica que estén en la misma red WiFi/LAN

### ❌ "Requiere permisos de administrador"
→ Haz clic derecho → "Ejecutar como administrador"

### ❌ "Firewall bloquea"
→ El script lo configura automáticamente  
→ Si falla, ver `GUIA_CONFIGURACION_PASO_A_PASO.md`

---

## 📞 AYUDA

Si tienes problemas:
1. Lee `GUIA_CONFIGURACION_PASO_A_PASO.md`
2. Ejecuta `test_multiusuario.py` para diagnóstico
3. Verifica la sección "Solución de problemas"

---

## 🎯 RESUMEN

**Tiempo total estimado:** 15-20 minutos para 4 PCs

**Resultado:**
✅ Todos los PCs comparten la misma base de datos  
✅ Cambios en tiempo real  
✅ Sin pérdida de datos  
✅ Sistema centralizado  

---

**¡Comienza con el PASO 1!** 🚀
