# 📦 Vithas Avisos - Ejecutable Portable

## 🚀 Cómo Crear el Ejecutable

### Opción 1: Script Automático (Recomendado)
1. Haz doble clic en `build_portable.bat`
2. Espera a que termine (puede tardar 3-5 minutos)
3. El ejecutable estará en la carpeta `dist\Vithas_Avisos\`

### Opción 2: Manual
```bash
pyinstaller build_portable.bat
```

## 📂 Distribución

Una vez creado el ejecutable:

1. **Carpeta completa**: `dist\Vithas_Avisos\`
   - Contiene `Vithas_Avisos.exe` y todas las dependencias
   - **Copia toda esta carpeta** a cualquier PC Windows
   - No requiere instalación de Python ni librerías

2. **Tamaño aproximado**: 150-300 MB (incluye Python, PyQt6, matplotlib, etc.)

## ✅ Requisitos del PC Destino

- **Sistema Operativo**: Windows 10/11 (64-bit)
- **RAM**: Mínimo 4GB recomendado
- **Espacio**: ~500MB libres
- **NO requiere**:
  - ❌ Python instalado
  - ❌ Librerías adicionales
  - ❌ Permisos de administrador (para ejecutar)

## 🎯 Cómo Usar el Ejecutable

1. Copia la carpeta `Vithas_Avisos` completa al PC destino
2. Haz doble clic en `Vithas_Avisos.exe`
3. ¡Listo! La aplicación se ejecutará

## 🔧 Configuración

### Base de Datos PostgreSQL
Si usas PostgreSQL, asegúrate de:
1. Copiar el archivo `.env` con las credenciales correctas
2. O editar `.env` en la carpeta del ejecutable antes de ejecutar

### Archivos de Datos
Los siguientes archivos deben estar en la misma carpeta que el .exe:
- `avisos.csv` - Datos de avisos
- `hoteles.csv` - Listado de hoteles
- `medicos.csv` - Listado de médicos
- `teams_config.json` - Configuración de Teams
- `logo.png` y `vithas_bg.png` - Recursos visuales

## 🐛 Solución de Problemas

### Error: "No se puede iniciar la aplicación"
- Verifica que todos los archivos .csv y .json estén presentes
- Comprueba que el archivo `.env` tenga las credenciales correctas

### Error: "Falta VCRUNTIME140.dll"
- Descarga e instala: [Microsoft Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)

### La aplicación se cierra inmediatamente
- Ejecuta desde CMD para ver errores:
  ```cmd
  cd ruta\a\Vithas_Avisos
  Vithas_Avisos.exe
  ```

## 📝 Notas Importantes

1. **Primera ejecución**: Puede tardar un poco más en cargar
2. **Antivirus**: Algunos antivirus pueden marcar falsos positivos en ejecutables de PyInstaller
3. **Actualizaciones**: Para actualizar, simplemente reemplaza la carpeta completa con la nueva versión

## 🔐 Credenciales de Login

Por defecto:
- **Usuario**: `IISS`
- **Contraseña**: `IISS2025`

## 📞 Soporte

Para problemas o dudas, contacta al administrador del sistema.

---

**Versión**: 1.0  
**Fecha**: 2026-01-01  
**Desarrollado para**: Vithas
