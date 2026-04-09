# ✅ EJECUTABLE CREADO EXITOSAMENTE

## 📍 Ubicación del Ejecutable

**Ruta**: `c:\Users\Ayoub\Desktop\Proyecto_Avisos\dist\Vithas_Avisos\`

**Archivo principal**: `Vithas_Avisos.exe` (20.1 MB)

## 🚀 Cómo Usar

### Para ejecutar en ESTE PC:
1. Ve a la carpeta: `dist\Vithas_Avisos\`
2. Haz doble clic en `Vithas_Avisos.exe`
3. ¡Listo!

### Para distribuir a OTROS PCs:
1. **Copia TODA la carpeta** `dist\Vithas_Avisos\` (no solo el .exe)
2. Pégala en el PC destino (USB, red, email, etc.)
3. Ejecuta `Vithas_Avisos.exe` en el PC destino
4. **NO requiere instalación de Python ni librerías**

## 📦 Contenido de la Carpeta

```
Vithas_Avisos/
├── Vithas_Avisos.exe       ← Ejecutable principal
├── _internal/              ← Dependencias (DLLs, librerías)
├── avisos.csv              ← Datos de avisos
├── hoteles.csv             ← Datos de hoteles
├── medicos.csv             ← Datos de médicos
├── logo.png                ← Logo Vithas
├── vithas_bg.png           ← Fondo
├── teams_config.json       ← Config Teams
├── hoteles_coords.json     ← Coordenadas hoteles
└── .env                    ← Configuración DB
```

## ⚠️ IMPORTANTE

### ✅ Debes copiar:
- **TODA la carpeta** `Vithas_Avisos` completa
- No solo el archivo .exe

### ❌ NO funciona si:
- Solo copias el .exe sin la carpeta `_internal`
- Faltan los archivos .csv o .json

## 🎯 Requisitos del PC Destino

✅ Windows 10 o 11 (64-bit)  
✅ 4GB RAM mínimo  
✅ 500MB espacio libre  
❌ NO requiere Python instalado  
❌ NO requiere librerías adicionales  
❌ NO requiere permisos de administrador  

## 🔐 Credenciales de Acceso

- **Usuario**: `IISS`
- **Contraseña**: `IISS2025`

## 🔧 Opciones Adicionales

### Opción 1: Ejecutable de Carpeta (ACTUAL - Recomendado)
✅ Inicio rápido (2-3 segundos)  
✅ Tamaño total: ~150-200 MB  
❌ Requiere copiar carpeta completa  

**Ya creado en**: `dist\Vithas_Avisos\`

### Opción 2: Ejecutable de Un Solo Archivo
✅ Un solo archivo .exe (fácil de distribuir)  
✅ No necesita carpeta de dependencias  
❌ Inicio lento (10-30 segundos)  
❌ Archivo más grande (~300-400 MB)  

**Para crear**: Ejecuta `build_onefile.bat`

## 📝 Notas

1. **Primera ejecución**: Puede tardar unos segundos extra
2. **Antivirus**: Algunos pueden dar falsa alarma (es normal con PyInstaller)
3. **Base de datos**: Si usas PostgreSQL, verifica el archivo `.env`
4. **Actualizaciones**: Para actualizar, reemplaza toda la carpeta

## 🐛 Solución de Problemas

### "No se encuentra VCRUNTIME140.dll"
Instala: https://aka.ms/vs/17/release/vc_redist.x64.exe

### "La aplicación no inicia"
1. Verifica que todos los archivos .csv estén presentes
2. Comprueba el archivo `.env` si usas PostgreSQL
3. Ejecuta desde CMD para ver errores:
   ```cmd
   cd dist\Vithas_Avisos
   Vithas_Avisos.exe
   ```

### "Antivirus bloquea el ejecutable"
- Es un falso positivo común con PyInstaller
- Añade excepción en el antivirus
- O usa certificado digital (avanzado)

## 📊 Tamaño Total

- **Ejecutable**: 20.1 MB
- **Dependencias (_internal)**: ~150-180 MB
- **Datos (CSV, JSON, imágenes)**: ~1-2 MB
- **TOTAL**: ~170-200 MB

## ✨ Características Incluidas

✅ Interfaz gráfica completa (PyQt6)  
✅ Gráficos y estadísticas (Matplotlib)  
✅ Mapas interactivos (Folium)  
✅ Conexión PostgreSQL (opcional)  
✅ Exportación Excel/CSV  
✅ Integración Teams/WhatsApp
✅ Todos los recursos visuales  

---

**¡Disfruta de tu aplicación portable!** 🚀

Para crear versiones futuras, simplemente ejecuta `build_portable.bat` de nuevo.
