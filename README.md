

<h1 align="center">🏥 Vithas Medical Manager</h1>

<p align="center">
  <strong>Sistema de Gestión de Avisos Médicos para Vithas Xanit — Costa del Sol</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/PyQt6-6.x-41CD52?style=for-the-badge&logo=qt&logoColor=white" alt="PyQt6"/>
  <img src="https://img.shields.io/badge/PostgreSQL-15+-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL"/>
  <img src="https://img.shields.io/badge/License-Privado-red?style=for-the-badge" alt="License"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Estado-En%20Producción-brightgreen?style=flat-square" alt="Status"/>
  <img src="https://img.shields.io/badge/Plataforma-Windows-0078D6?style=flat-square&logo=windows&logoColor=white" alt="Platform"/>
  <img src="https://img.shields.io/badge/Integración-Microsoft%20Teams-6264A7?style=flat-square&logo=microsoftteams&logoColor=white" alt="Teams"/>
</p>

---

## 📖 Descripción

**Vithas Medical Manager** es una aplicación de escritorio profesional diseñada para la gestión integral de avisos médicos en el Hospital Vithas Xanit (Costa del Sol). Permite registrar, rastrear y coordinar notificaciones médicas provenientes de hoteles, facilitando la atención urgente a pacientes turistas.

### ¿Qué problema resuelve?

En la Costa del Sol, los turistas alojados en hoteles pueden necesitar atención médica urgente. Este sistema centraliza todo el flujo:

```
🏨 Hotel → 📞 Aviso → 👨‍⚕️ Médico asignado → 🚑 Traslado → 🏥 Ingreso
```

---

## ✨ Funcionalidades principales

### 📋 Gestión de avisos
- Registro completo de avisos médicos con datos del paciente, hotel, médico y diagnóstico
- Estados de seguimiento: **Abierto**, **Cerrado**, **Anulado**
- Validaciones automáticas (NHC obligatorio en traslados, campos requeridos, etc.)
- Bloqueo de edición en avisos cerrados para preservar integridad

### 🏨 Gestión de hoteles
- Base de datos de hoteles con geolocalización automática
- Cálculo de distancia al hospital basado en municipio
- Mapa interactivo con **OpenStreetMap + Folium**
- Detección automática de municipio y zona de aviso

### 👨‍⚕️ Directorio de médicos
- Gestión del directorio con nombre y teléfono
- Asignación automática de teléfono al seleccionar médico

### 📊 Estadísticas y Dashboard
- Gráficos con **Matplotlib** integrado
- Visualización de datos por fecha, hotel, nacionalidad
- Métricas de atención y traslados

### 🔔 Integración con Microsoft Teams
- Notificaciones automáticas via **Power Automate** webhooks
- Tarjetas adaptativas con datos del aviso
- Envío asíncrono sin bloquear la interfaz

### 📤 Exportación
- Exportación a **Excel (.xlsx)** y **LibreOffice (.ods)**
- Columnas calculadas automáticamente (municipio, zona)
- Filtros por fecha y estado

---

## 🎨 Temas visuales

La aplicación incluye **5 temas** con cambio instantáneo:

| Tema | Descripción |
|------|-------------|
| 🌑 **Neon** | Fondo oscuro con acentos azul neón — alto contraste |
| ☀️ **Light** | Estilo claro tipo Material Design — ambientes iluminados |
| 🏥 **Vithas** | Colores corporativos con fondo institucional semi-transparente |
| 🪨 **Graphite** | Gris oscuro elegante — reduce fatiga visual |
| 🌲 **Forest** | Tonos verdes naturales — estilo relajante |

---

## 🛠️ Tecnologías

| Tecnología | Uso |
|-----------|-----|
| **Python 3.10+** | Lenguaje principal |
| **PyQt6** | Interfaz gráfica de escritorio |
| **PostgreSQL** | Base de datos relacional (multi-usuario) |
| **psycopg2** | Driver de conexión a PostgreSQL |
| **pandas** | Manipulación y exportación de datos |
| **Matplotlib** | Gráficos y estadísticas |
| **Folium** | Mapas interactivos |
| **Requests** | Integración con Teams via webhooks |

---

## 📁 Estructura del proyecto

```
Proyecto_Avisos/
├── main.py                     # Aplicación principal (PyQt6)
├── requirements.txt            # Dependencias Python
├── .env.template               # Plantilla de configuración
├── setup_database.sql          # Script de creación de BD
│
├── src/
│   ├── database.py             # Conexión y queries PostgreSQL
│   ├── teams_sender.py         # Notificaciones a Microsoft Teams
│   ├── teams_config.py         # Configuración de webhooks
│   └── migrate_csv_to_db.py    # Migración de CSV a PostgreSQL
│
├── logo.png                    # Logo de la aplicación
├── vithas_bg.png               # Fondo para el tema Vithas
└── config_gear.png             # Icono de configuración
```

---

## 🚀 Instalación

### Prerrequisitos

- Python 3.10 o superior
- PostgreSQL 15 o superior
- Windows 10/11

### 1. Clonar el repositorio

```bash
git clone https://github.com/khiraniayoub/AvisosMedicos.git
cd AvisosMedicos
```

### 2. Crear entorno virtual

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar la base de datos

Copia la plantilla de variables de entorno y configúrala:

```bash
copy .env.template .env
```

Edita `.env` con tus credenciales de PostgreSQL:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=avisos_db
DB_USER=postgres
DB_PASSWORD=tu_contraseña_segura
```

Ejecuta el script SQL para crear las tablas:

```bash
psql -U postgres -f setup_database.sql
```

### 5. Ejecutar la aplicación

```bash
python main.py
```

---

## ⚙️ Configuración adicional

### Microsoft Teams (opcional)

Para activar las notificaciones a Teams:

1. Crea un flujo de Power Automate con trigger "When a Teams webhook request is received"
2. Crea un archivo `teams_config.json` en la raíz del proyecto:

```json
{
  "destinations": [
    {
      "name": "Canal de avisos",
      "url": "TU_WEBHOOK_URL_AQUI"
    }
  ]
}
```

### Modo multi-usuario

Para configurar acceso desde varios PCs en la misma red:

1. Configura PostgreSQL para aceptar conexiones remotas
2. Cada cliente necesita su propio `.env` apuntando al servidor:

```env
DB_HOST=192.168.x.x
DB_PORT=5432
DB_NAME=avisos_db
DB_USER=postgres
DB_PASSWORD=contraseña
```

---

## 📸 Capturas de pantalla

> *Próximamente se añadirán capturas de los diferentes temas y funcionalidades.*

---

## 🗺️ Roadmap

- [ ] Búsqueda avanzada global
- [ ] Sistema de notificaciones con alertas temporales
- [ ] Backup automático programado
- [ ] Impresión/exportación a PDF con logo
- [ ] Atajos de teclado
- [ ] Historial de cambios y auditoría
- [ ] Plantillas de diagnóstico con autocompletado
- [ ] Versión web responsive

---

## 👤 Autor

**Ayoub Khirani**

- GitHub: [@khiraniayoub](https://github.com/khiraniayoub)

---

## 📄 Licencia

Este proyecto es de **uso privado**.