import sys
import csv
import os
import shutil
import json

from pathlib import Path
from io import BytesIO
import pandas as pd
import requests
from PyQt6.QtCore import QDate, QTime, Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QAbstractAnimation, QPoint, QRect, QUrl
from PyQt6.QtGui import QColor, QPixmap, QCursor
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QFormLayout, QLineEdit, QComboBox, QDateEdit, QTimeEdit, 
                             QSpinBox, QTextEdit, QCheckBox, QPushButton, QLabel, 
                             QScrollArea, QMessageBox, QTabWidget, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QFrame, QMenu, QGridLayout,
                             QFileDialog, QGraphicsDropShadowEffect, QDialog)

import webbrowser
from urllib.parse import quote
import math

# Matplotlib for charts
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# Folium for interactive maps
import folium
from folium import plugins

# Try to import QWebEngineView for map display
try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    WEBENGINE_AVAILABLE = True
except ImportError:
    WEBENGINE_AVAILABLE = False
    QWebEngineView = None

# (Removed image generation - schematic summaries are HTML-based)

class ClickableLabel(QLabel):
    clicked = pyqtSignal()
    
    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

def get_vithas_stylesheet():
    return """
    QMainWindow {
        border-image: url(vithas_bg.png) 0 0 0 0 stretch stretch;
    }
    QWidget {
        font-family: 'Segoe UI', 'Roboto', sans-serif;
        font-size: 13px;
    }
    /* Make panels semi-transparent white/grey to be readable over image */
    QTabWidget::pane {
        border: 2px solid #0055a4; /* Vithas Blue-ish */
        background-color: rgba(255, 255, 255, 0.3);
        border-radius: 8px;
    }
    QTabBar::tab {
        background: rgba(255, 255, 255, 0.6);
        color: #0055a4;
        padding: 10px 20px;
        margin-right: 4px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        font-weight: bold;
    }
    QTabBar::tab:selected {
        background: #0055a4;
        color: white;
    }
    QLabel {
        color: #0055a4;
        font-weight: bold;
    }
    QLineEdit, QComboBox, QDateEdit, QTimeEdit, QSpinBox, QTextEdit {
        background-color: rgba(255, 255, 255, 0.9);
        border: 1px solid #aaa;
        border-radius: 4px;
        padding: 5px;
        color: #333;
        selection-background-color: #0055a4;
    }
    QTableWidget {
        background-color: rgba(255, 255, 255, 0.45);
        gridline-color: #ccc;
        color: #000;
        font-weight: bold;
    }
    QHeaderView::section {
        background-color: #0055a4;
        color: white;
        padding: 5px;
        border: none;
    }
    QPushButton {
        background-color: #0055a4;
        color: white;
        border-radius: 5px;
        padding: 8px 15px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #004488;
    }

    /* --- CUSTOM COMPONENT STYLES (Vithas Mode) --- */
    
    QLabel#HeaderLabel {
        color: #0055a4;
        font-size: 16px; 
        font-weight: bold; 
        text-transform: uppercase; 
        border-bottom: 2px solid #0055a4; 
        padding-bottom: 5px;
        margin-top: 15px;
    }

    QLabel#EstadoLabel {
        color: #0055a4; 
        font-size: 18px; 
        font-weight: 800; 
        margin-bottom: 2px; 
        text-transform: uppercase;
    }

    QComboBox#EstadoCombo {
        font-weight: 800; 
        font-size: 18px; 
        color: white; /* White text on blue bg usually, but here background is light in Vithas mode? No, Vithas mode inputs are white bg. */
        color: #0055a4; /* Blue text */
        padding: 8px 12px;
        border: 2px solid #0055a4;
        border-radius: 8px;
        background-color: rgba(0, 85, 164, 0.12);
        text-transform: uppercase;
    }

    QCheckBox#TrasladoCheck {
        font-weight: bold; 
        font-size: 14px; 
        color: #0055a4;
        padding: 8px;
        border: 2px solid #0055a4;
        border-radius: 6px;
        background-color: rgba(0, 85, 164, 0.1);
    }
    """

def get_neon_stylesheet():
    return """
    QMainWindow, QWidget {
        background-color: #050505; /* Deep Black */
        color: #e0e0e0;
        font-family: 'Segoe UI', 'Roboto', sans-serif;
        font-size: 13px;
    }

    /* --- Tabs --- */
    QTabWidget::pane {
        border: 2px solid #00f3ff;
        background-color: #0d0d0d;
        top: -1px;
        border-radius: 4px;
    }
    QTabBar::tab {
        background: #101014;
        color: #00f3ff;
        padding: 12px 25px;
        margin-right: 4px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        font-weight: bold;
        text-transform: uppercase;
        border: 1px solid #333;
        border-bottom: none;
    }
    QTabBar::tab:selected {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1a1a2e, stop:1 #00f3ff);
        color: #000;
        border: 2px solid #00f3ff;
        border-bottom: 2px solid #0d0d0d;
    }
    QTabBar::tab:hover {
        background: #1a1a25;
        color: white;
        border-color: #bc13fe;
    }

    /* --- Group/Headers --- */
    QGroupBox {
        border: 2px solid #333;
        border-radius: 6px;
        margin-top: 20px;
        font-weight: bold;
        color: #00f3ff;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top center;
        padding: 0 10px;
        background-color: #050505; 
    }

    /* --- Inputs --- */
    QLineEdit, QComboBox, QDateEdit, QTimeEdit, QSpinBox, QTextEdit {
        background-color: #101014;
        border: 1px solid #333;
        border-radius: 6px;
        color: #ffffff;
        padding: 8px;
        font-size: 13px;
    }
    QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QDateEdit:focus, QTimeEdit:focus, QSpinBox:focus {
        border: 2px solid #00f3ff;
        background-color: #1a1a25;
        selection-background-color: #00f3ff;
        selection-color: black;
    }

    /* --- Buttons --- */
    QPushButton {
        background-color: #101014;
        border: 1px solid #00f3ff;
        color: #00f3ff;
        padding: 10px 20px;
        border-radius: 6px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #00f3ff;
        color: #000000;
    }
    QPushButton:pressed {
        background-color: #0099aa;
        border-color: #0099aa;
    }
    
    QPushButton#DeleteBtn {
         border: 1px solid #ff0055;
         color: #ff0055;
    }
    QPushButton#DeleteBtn:hover {
        background-color: #ff0055;
        color: white;
    }

    QPushButton#TelegramBtn {
        border: 1px solid #2AABEE;
        color: #2AABEE;
    }
    QPushButton#TelegramBtn:hover {
        background-color: #2AABEE;
        color: white;
    }

    /* --- Tables --- */
    QTableWidget {
        background-color: #0d0d0d;
        gridline-color: #333;
        color: #f0f0f0;
        selection-background-color: #00f3ff;
        selection-color: #000000;
        border: none;
    }
    QHeaderView::section {
        background-color: #101014;
        color: #00f3ff;
        padding: 8px;
        border: 1px solid #333;
        font-weight: bold;
        text-transform: uppercase;
    }
    QHeaderView::section:horizontal {
        border-bottom: 2px solid #00f3ff;
    }

    /* --- Scrollbars --- */
    QScrollBar:vertical {
        background: #050505;
        width: 12px;
    }
    QScrollBar::handle:vertical {
        background: #333;
        border-radius: 6px;
        min-height: 20px;
    }
    QScrollBar::handle:vertical:hover {
        background: #00f3ff;
    }
    
    /* --- Checkbox --- */
    QCheckBox {
        color: #e0e0e0;
        spacing: 10px;
    }
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border: 1px solid #555;
        border-radius: 4px;
        background: #101014;
    }
    QCheckBox::indicator:checked {
        background-color: #00f3ff;
        border-color: #00f3ff;
    }

    /* --- CUSTOM COMPONENT STYLES (Migrated from inline) --- */
    
    QLabel#HeaderLabel {
        color: #00f3ff;
        font-size: 16px; 
        font-weight: bold; 
        text-transform: uppercase; 
        border-bottom: 2px solid #00f3ff; 
        padding-bottom: 5px;
        margin-top: 15px; /* applied to both generally, though medicos needs it specifically */
    }

    QLabel#EstadoLabel {
        color: #00f3ff; 
        font-size: 18px; 
        font-weight: 800; 
        margin-bottom: 2px; 
        text-transform: uppercase;
    }

    QComboBox#EstadoCombo {
        font-weight: 800; 
        font-size: 18px; 
        color: #00f3ff;
        padding: 8px 12px;
        border: 2px solid #00f3ff;
        border-radius: 8px;
        background-color: rgba(0, 243, 255, 0.12);
        text-transform: uppercase;
    }

    QCheckBox#TrasladoCheck {
        font-weight: bold; 
        font-size: 14px; 
        color: #00f3ff;
        padding: 8px;
        border: 2px solid #00f3ff;
        border-radius: 6px;
        background-color: rgba(0, 243, 255, 0.1);
    }
    """

def get_light_stylesheet():
    return """
    QMainWindow, QWidget {
        background-color: #f0f2f5;
        color: #1d2129;
        font-family: 'Segoe UI', 'Roboto', sans-serif;
        font-size: 13px;
    }
    
    /* --- Tabs --- */
    QTabWidget::pane {
        border: 1px solid #ddd;
        border-radius: 6px;
        background-color: #ffffff;
        top: -1px; 
    }
    QTabBar::tab {
        background: #e4e6eb;
        color: #606770;
        padding: 10px 20px;
        margin-right: 4px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        font-weight: 600;
        border: 1px solid #ddd;
        border-bottom: none;
    }
    QTabBar::tab:selected {
        background: #ffffff;
        color: #1877f2;
        border-bottom: 2px solid #1877f2;
    }
    QTabBar::tab:hover {
        background: #f2f3f5;
        color: #1877f2;
    }

    /* --- Labels --- */
    QLabel {
        color: #4b4f56;
        font-weight: bold;
    }

    /* --- Inputs --- */
    QLineEdit, QComboBox, QDateEdit, QTimeEdit, QSpinBox, QTextEdit {
        background-color: #ffffff;
        border: 1px solid #ccd0d5;
        border-radius: 4px;
        color: #1d2129;
        padding: 6px;
    }
    QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QDateEdit:focus, QTimeEdit:focus, QSpinBox:focus {
        border: 1px solid #1877f2;
        background-color: #fff;
    }

    /* --- Buttons --- */
    QPushButton {
        background-color: #1877f2;
        border: 1px solid #1877f2;
        color: white;
        padding: 8px 16px;
        border-radius: 4px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #166fe5;
    }
    QPushButton:pressed {
        background-color: #1464cf;
    }
    
    QPushButton#DeleteBtn {
         background-color: #fff;
         color: #e41e3f;
         border: 1px solid #e41e3f;
    }
    QPushButton#DeleteBtn:hover {
        background-color: #e41e3f;
        color: white;
    }

    /* --- Table --- */
    QTableWidget {
        background-color: #ffffff;
        gridline-color: #f0f2f5;
        color: #1d2129;
        selection-background-color: #e7f3ff;
        selection-color: #1877f2;
    }
    QHeaderView::section {
        background-color: #f7f8fa;
        color: #4b4f56;
        padding: 5px;
        border: 1px solid #ddd;
    }

    QScrollBar:vertical {
        background: #f0f2f5;
        width: 12px;
    }
    QScrollBar::handle:vertical {
        background: #bcc0c4;
        border-radius: 6px;
    }
    
    QCheckBox {
        color: #1877f2;
    }
    """


class HotelLocationManager:
    """Helper to detect Municipio and Zona based on Hotel name."""
    
    ZONA_OCCIDENTAL = "ZONA COSTA OCCIDENTAL"
    ZONA_ORIENTAL = "ZONA COSTA ORIENTAL"
    ZONA_MALAGA = "ZONA MALAGA"
    
    # Specific Hotel Rules: (Hotel Keyword, Municipio, Zona)
    # These override general location rules
    HOTEL_RULES = [
        # --- MARBELLA ---
        ("Amare", "Marbella", ZONA_OCCIDENTAL),
        ("Don Carlos", "Marbella", ZONA_OCCIDENTAL),
        ("El Fuerte", "Marbella", ZONA_OCCIDENTAL),
        ("Eurostars Oasis", "Marbella", ZONA_OCCIDENTAL),
        ("Hard Rock", "Marbella", ZONA_OCCIDENTAL),
        ("Coral Beach", "Marbella", ZONA_OCCIDENTAL),
        ("Claude", "Marbella", ZONA_OCCIDENTAL),
        ("Don Pepe", "Marbella", ZONA_OCCIDENTAL),
        ("Puente Romano", "Marbella", ZONA_OCCIDENTAL),
        ("Lima", "Marbella", ZONA_OCCIDENTAL),
        ("Nobu", "Marbella", ZONA_OCCIDENTAL),
        ("Boho Club", "Marbella", ZONA_OCCIDENTAL),
        ("Los Monteros", "Marbella", ZONA_OCCIDENTAL),
        ("Guadalpin", "Marbella", ZONA_OCCIDENTAL),
        ("Senator Marbella", "Marbella", ZONA_OCCIDENTAL),
        ("NH Marbella", "Marbella", ZONA_OCCIDENTAL),
        ("Barcelo Marbella", "Marbella", ZONA_OCCIDENTAL),
        ("San Pedro", "Marbella", ZONA_OCCIDENTAL),
        ("Puerto Banus", "Marbella", ZONA_OCCIDENTAL),
        ("Banus", "Marbella", ZONA_OCCIDENTAL),
        
        # --- ESTEPONA ---
        ("Kempinski", "Estepona", ZONA_OCCIDENTAL),
        ("El Pilar", "Estepona", ZONA_OCCIDENTAL),
        ("Estepona Plaza", "Estepona", ZONA_OCCIDENTAL),
        ("H10 Estepona", "Estepona", ZONA_OCCIDENTAL),
        ("Elba Estepona", "Estepona", ZONA_OCCIDENTAL),
        ("Sol Marbella Estepona", "Estepona", ZONA_OCCIDENTAL),
        ("METT", "Estepona", ZONA_OCCIDENTAL),
        ("Exe Estepona", "Estepona", ZONA_OCCIDENTAL),
        
        # --- FUENGIROLA ---
        ("IPV Palace", "Fuengirola", ZONA_OCCIDENTAL),
        ("Ilunion Fuengirola", "Fuengirola", ZONA_OCCIDENTAL),
        ("Leonardo", "Fuengirola", ZONA_OCCIDENTAL),
        ("Yaramar", "Fuengirola", ZONA_OCCIDENTAL),
        ("Angela", "Fuengirola", ZONA_OCCIDENTAL),
        ("El Puerto", "Fuengirola", ZONA_OCCIDENTAL),
        ("Casa Consistorial", "Fuengirola", ZONA_OCCIDENTAL),
        ("Las Palmeras", "Fuengirola", ZONA_OCCIDENTAL),
        ("Occidental Fuengirola", "Fuengirola", ZONA_OCCIDENTAL),
        ("Veramar", "Fuengirola", ZONA_OCCIDENTAL),
        ("Jabega", "Fuengirola", ZONA_OCCIDENTAL),
        
        # --- BENALMADENA ---
        ("Alay", "Benalmádena", ZONA_OCCIDENTAL),
        ("Palladium", "Benalmádena", ZONA_OCCIDENTAL),
        ("Medplaya", "Benalmádena", ZONA_OCCIDENTAL),
        ("Siroco", "Benalmádena", ZONA_OCCIDENTAL),
        ("Riviera", "Benalmádena", ZONA_OCCIDENTAL),
        ("Triton", "Benalmádena", ZONA_OCCIDENTAL),
        ("Bali", "Benalmádena", ZONA_OCCIDENTAL),
        ("Best Benalmadena", "Benalmádena", ZONA_OCCIDENTAL),
        ("Estival", "Benalmádena", ZONA_OCCIDENTAL),
        ("Sunset Beach", "Benalmádena", ZONA_OCCIDENTAL),
        
        # --- TORREMOLINOS ---
        ("Bajondillo", "Torremolinos", ZONA_OCCIDENTAL),
        ("Riu Costa del Sol", "Torremolinos", ZONA_OCCIDENTAL),
        ("Perla del Sur", "Torremolinos", ZONA_OCCIDENTAL),
        ("Zen Airport", "Torremolinos", ZONA_OCCIDENTAL),
        ("Melia Costa del Sol", "Torremolinos", ZONA_OCCIDENTAL),
        ("Sol Principe", "Torremolinos", ZONA_OCCIDENTAL),
        ("Sol House", "Torremolinos", ZONA_OCCIDENTAL),
        ("Sol Don Pablo", "Torremolinos", ZONA_OCCIDENTAL),
        ("Sol Don Pedro", "Torremolinos", ZONA_OCCIDENTAL),
        ("Sol Don Marco", "Torremolinos", ZONA_OCCIDENTAL),
        ("Pezyespada", "Torremolinos", ZONA_OCCIDENTAL),
        ("Pez Espada", "Torremolinos", ZONA_OCCIDENTAL),
        ("Amaragua", "Torremolinos", ZONA_OCCIDENTAL),
        ("Tropicana", "Torremolinos", ZONA_OCCIDENTAL),
        
        # --- MIJAS ---
        ("Ilunion Hacienda", "Mijas", ZONA_OCCIDENTAL),
        ("La Cala", "Mijas", ZONA_OCCIDENTAL),
        ("Zambra", "Mijas", ZONA_OCCIDENTAL),
        ("TRH Mijas", "Mijas", ZONA_OCCIDENTAL),
        
        # --- MALAGA ---
        ("Miramar", "Málaga", ZONA_MALAGA),
        ("Castillo de Santa Catalina", "Málaga", ZONA_MALAGA),
        ("Vincci", "Málaga", ZONA_MALAGA),
        ("Posada del Patio", "Málaga", ZONA_MALAGA),
        ("Larios", "Málaga", ZONA_MALAGA),
        ("Molina Lario", "Málaga", ZONA_MALAGA),
        ("Don Curro", "Málaga", ZONA_MALAGA),
        ("AC Hotel Malaga", "Málaga", ZONA_MALAGA),
        ("Barcelo Malaga", "Málaga", ZONA_MALAGA),
        ("Eurostars Malaga", "Málaga", ZONA_MALAGA),
        ("Ilunion Malaga", "Málaga", ZONA_MALAGA),
        ("Salles", "Málaga", ZONA_MALAGA),
        ("Guadalmedina", "Málaga", ZONA_MALAGA),
        ("Zeus", "Málaga", ZONA_MALAGA),
        ("Sur Málaga", "Málaga", ZONA_MALAGA),
        ("Sur Malaga", "Málaga", ZONA_MALAGA),
        ("Palacete", "Málaga", ZONA_MALAGA),
        ("Goartin", "Málaga", ZONA_MALAGA),
        ("Goartín", "Málaga", ZONA_MALAGA),
        ("Vibes", "Málaga", ZONA_MALAGA),
        
        # --- NERJA/AXARQUIA ---
        ("Carabeo", "Nerja", ZONA_ORIENTAL),
        ("Balcon de Europa", "Nerja", ZONA_ORIENTAL),
        ("Parador de Nerja", "Nerja", ZONA_ORIENTAL),
        ("Riu Monica", "Nerja", ZONA_ORIENTAL),
        ("Perla Marina", "Nerja", ZONA_ORIENTAL),
        ("La Casa", "Torrox", ZONA_ORIENTAL),
        ("Iberostar Malaga Playa", "Torrox", ZONA_ORIENTAL),
        ("Baviera", "Vélez-Málaga", ZONA_ORIENTAL),
        
        # --- FALLBACKS BY NAME ---
        ("Marbella", "Marbella", ZONA_OCCIDENTAL),
        ("Estepona", "Estepona", ZONA_OCCIDENTAL),
        ("Benahavis", "Benahavís", ZONA_OCCIDENTAL),
        ("Casares", "Casares", ZONA_OCCIDENTAL),
        ("Manilva", "Manilva", ZONA_OCCIDENTAL),
        ("Sotogrande", "San Roque", ZONA_OCCIDENTAL),
        ("Fuengirola", "Fuengirola", ZONA_OCCIDENTAL),
        ("Mijas", "Mijas", ZONA_OCCIDENTAL),
        ("Benalmadena", "Benalmádena", ZONA_OCCIDENTAL),
        ("Torremolinos", "Torremolinos", ZONA_OCCIDENTAL),
        ("Malaga", "Málaga", ZONA_MALAGA),
        ("Málaga", "Málaga", ZONA_MALAGA),
        ("Rincon", "Rincón de la Victoria", ZONA_ORIENTAL),
        ("Velez", "Vélez-Málaga", ZONA_ORIENTAL),
        ("Torre del Mar", "Vélez-Málaga", ZONA_ORIENTAL),
        ("Nerja", "Nerja", ZONA_ORIENTAL),
        ("Torrox", "Torrox", ZONA_ORIENTAL),
        ("Frigiliana", "Frigiliana", ZONA_ORIENTAL),
        ("Almuñecar", "Almuñécar", ZONA_ORIENTAL),
        ("Almuñécar", "Almuñécar", ZONA_ORIENTAL),
    ]

    @classmethod
    def get_location(cls, hotel_name):
        if not hotel_name:
            return "", ""
        
        normalized = hotel_name.lower()
        
        # Check specific rules first
        for keyword, municipio, zona in cls.HOTEL_RULES:
            if keyword.lower() in normalized:
                return municipio, zona
        
        # Default fallback
        return "PENDIENTE", "PENDIENTE"

# Approximate coordinates (lat, lon) for municipios.
# Used to compute distance to Vithas Xanit (Benalmádena).
HOSPITAL_XANIT_COORD = (36.5722, -4.5667)  # Vithas Xanit Benalmádena

MUNICIPIO_COORDS = {
    # COSTA OCCIDENTAL
    "Manilva": (36.3126, -5.2463),
    "Casares": (36.4092, -5.1833),
    "Estepona": (36.4277, -5.1454),
    "Benahavís": (36.4858, -4.9494),
    "Benahavis": (36.4858, -4.9494),
    "San Pedro": (36.4878, -4.9904), # San Pedro Alcántara
    "Marbella": (36.5090, -4.8828),
    "Mijas": (36.5950, -4.6410),
    "Fuengirola": (36.5394, -4.6243),
    "Benalmádena": (36.5722, -4.5667),
    "Benalmadena": (36.5722, -4.5667),
    "Torremolinos": (36.6245, -4.4999),
    "San Roque": (36.2942, -5.3396),
    
    # MALAGA
    "Málaga": (36.7213, -4.4214),
    "Malaga": (36.7213, -4.4214),
    
    # COSTA ORIENTAL
    "Rincón de la Victoria": (36.7436, -4.1646),
    "Vélez-Málaga": (36.7569, -4.1003),
    "Torre del Mar": (36.7410, -4.0955),
    "Torrox": (36.7093, -3.9236),
    "Nerja": (36.7435, -3.8769),
    "Frigiliana": (36.7672, -3.8852),
    "Almuñécar": (36.7436, -3.6956),
}

def haversine_km(coord1, coord2):
    """Return distance in kilometers between two (lat, lon) points."""
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    # convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371.0  # Earth radius in km
    return r * c

# Simple local cache for geocoded hotel coordinates
COORDS_CACHE_FILE = Path("hoteles_coords.json")

def load_coords_cache():
    if COORDS_CACHE_FILE.is_file():
        try:
            return json.loads(COORDS_CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def save_coords_cache(cache: dict):
    try:
        COORDS_CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass

def geocode_hotel(hotel_name: str):
    """Query Nominatim to get lat/lon for a hotel name. Returns (lat, lon) or None."""
    if not hotel_name:
        return None

    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": f"{hotel_name}, Málaga, Spain", "format": "json", "limit": 1}
    headers = {"User-Agent": "ProyectoAvisos/1.0 (Ayoub)"}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            if data:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                return (lat, lon)
    except Exception:
        return None
    return None


def create_schematic_html(data: dict) -> str:
    """Return a concise schematic HTML showing all relevant fields."""
    # Pull fields with safe defaults
    fecha = data.get("Fecha", "-")
    emisor = data.get("Emisor", "-")
    estado = (data.get("Estado", "") or "Pendiente")
    paciente = data.get("Paciente", "(sin nombre)")
    nacionalidad = data.get("Nacionalidad", "-")
    edad = data.get("Edad", "-")
    pagador = data.get("Pagador", "-")
    seguro = data.get("Seguro", "-")
    touroperador = data.get("Touroperador", "-")
    hora_aviso = data.get("Hora Avisos", data.get("Hora Aviso", "-"))
    hora_fin = data.get("Hora Finalización", data.get("Hora Finalizacion", "-"))
    medico = data.get("Medico", "-")
    diagnostico = data.get("Diagnostico", "-")
    nhc = data.get("Historia Medica", "-")
    traslado = (data.get("Traslado", "No") or "No")
    tipo_traslado = data.get("Tipo Traslado", "-")
    hora_ambulancia = data.get("Hora Ambulancia", "-")
    ingreso = (data.get("Ingreso", "No ingresa") or "No ingresa")
    medico_ingreso = data.get("Medico Ingreso", "-")

    # Colors
    estado_color = "#00cc66" if estado.lower() == "cerrado" else ("#ff4444" if estado.lower() == "abierto" else "#cccccc")
    traslado_color = "#ffcc00" if traslado.lower() in ("si", "sí", "yes", "true") else "#555555"
    
    # Determine ingreso color based on type
    if "uci" in str(ingreso).lower():
        ingreso_color = "#ff4444"  # Red for UCI
    elif "planta" in str(ingreso).lower():
        ingreso_color = "#ff9900"  # Orange for Planta
    else:
        ingreso_color = "#555555"  # Gray for No ingresa

    html = [
        "<div style='font-family:Segoe UI, Roboto, sans-serif; font-size:14px; color:#e6e6e6;'>",
        # Header row with fecha/emisor/estado
        "<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:12px'>",
        f"<div style='font-weight:700;font-size:18px'>{fecha} — {emisor}</div>",
        f"<div style='background:{estado_color};color:#000;padding:6px 10px;border-radius:8px;font-weight:700'>{estado}</div>",
        "</div>",

        # Main facts grid (two columns)
        "<table style='width:100%;border-collapse:collapse;margin-top:6px'>",
        "<tr>",
        f"<td style='vertical-align:top;padding:8px;width:50%'><b>Paciente:</b> {paciente}<br/><b>NHC:</b> {nhc}<br/><b>Nacionalidad:</b> {nacionalidad}<br/><b>Edad:</b> {edad}<br/><b>Pagador:</b> {pagador} <small style='color:#aaa'>({seguro})</small></td>",
        f"<td style='vertical-align:top;padding:8px;width:50%'><b>TTOO:</b> {touroperador}<br/><b>Hora Aviso:</b> {hora_aviso}<br/><b>Hora Fin:</b> {hora_fin}<br/><b>Médico:</b> {medico}<br/><b>Diagnóstico:</b> {diagnostico}</td>",
        "</tr>",
        "</table>",

        # Traslado section
        "<div style='margin-top:12px;padding:10px;background:#0d0d0d;border-radius:8px'>",
        f"<div style='display:inline-block;background:{traslado_color};color:#000;padding:6px 12px;border-radius:6px;font-weight:700;margin-right:10px'>Traslado: {traslado}</div>",
    ]
    
    # Add traslado details if applicable
    if traslado.lower() in ("si", "sí", "yes", "true"):
        html.append(f"<span style='margin-left:10px'><b>Tipo:</b> {tipo_traslado}</span>")
        if hora_ambulancia and hora_ambulancia != "-":
            html.append(f"<span style='margin-left:15px'><b>Hora Amb.:</b> {hora_ambulancia}</span>")
    
    html.append("</div>")

    # Ingreso section
    html.extend([
        "<div style='margin-top:10px;padding:10px;background:#0d0d0d;border-radius:8px'>",
        f"<div style='display:inline-block;background:{ingreso_color};color:#000;padding:6px 12px;border-radius:6px;font-weight:700;margin-right:10px'>Ingreso: {ingreso}</div>",
    ])
    
    # Add ingreso details if applicable
    if ingreso and ingreso.lower() not in ("no ingresa", "no", "-"):
        html.append(f"<span style='margin-left:10px'><b>Médico Ingreso:</b> {medico_ingreso}</span>")
    
    html.extend([
        "</div>",
        "</div>",
    ])
    
    return '\n'.join(html)

class AvisoManager:
    FILE_NAME = "avisos.csv"
    FIELDS = [
        "Emisor", "Hora Solicitud", "Fecha", "Hotel", "Habitacion", "Estado", "Paciente", 
        "Edad", "Historia Medica", "Nacionalidad", "Motivo Urgencia", "Pagador", 
        "Seguro", "Touroperador", "Hora Aviso", "Hora Finalización", "Medico", "Diagnostico", "Traslado", 
        "Tipo Traslado", "Hora Ambulancia", "Ingreso", "Medico Ingreso", "Observaciones"
    ]

    @classmethod
    def load_avisos(cls):
        if not os.path.isfile(cls.FILE_NAME):
            return []
        try:
            with open(cls.FILE_NAME, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                data = list(reader)
                for idx, row in enumerate(data):
                    row['_id'] = idx 
                return data
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return []

    @classmethod
    def save_all(cls, avisos_list):
        try:
            if os.path.exists(cls.FILE_NAME):
                shutil.copy(cls.FILE_NAME, cls.FILE_NAME + ".bak")
            
            with open(cls.FILE_NAME, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=cls.FIELDS)
                writer.writeheader()
                for aviso in avisos_list:
                    cleaned = {k: v for k, v in aviso.items() if k in cls.FIELDS}
                    writer.writerow(cleaned)
            return True, "Datos guardados correctamente."
        except Exception as e:
            return False, str(e)

    @classmethod
    def create_aviso(cls, data):
        avisos = cls.load_avisos()
        avisos.append(data)
        return cls.save_all(avisos)

    @classmethod
    def update_aviso(cls, index, data):
        avisos = cls.load_avisos()
        if 0 <= index < len(avisos):
            avisos[index] = data
            return cls.save_all(avisos)
        return False, "Índice no encontrado."

    @classmethod
    def delete_aviso(cls, index):
        avisos = cls.load_avisos()
        if 0 <= index < len(avisos):
            del avisos[index]
            return cls.save_all(avisos)
        return False, "Índice no encontrado."

    @classmethod
    def export_to_excel(cls, filename):
        avisos = cls.load_avisos()
        if not avisos:
            return False, "No hay datos para exportar."
        
        # Define the target columns matching the ODS template
        # FECHA, TIPO EMISOR, EMISOR, HAB., TTOO, MOTIVO LLAMADA, NOMBRE PACIENTE, NHC A XANIT, MEDICO DE URGENCIAS, OBSERVACIONES, MUNICIPIOADA, ZONA AVISO
        
        export_data = []
        for a in avisos:
            def val(key):
                v = a.get(key, "")
                if v is None: return "N/A"
                s = str(v).strip()
                return s if s else "N/A"

            hotel_name = val("Hotel")
            municipio, zona = HotelLocationManager.get_location(hotel_name)

            row = {
                "FECHA": val("Fecha"),
                "TIPO EMISOR": val("Emisor"),
                "EMISOR": hotel_name,
                "HAB.": val("Habitacion"), 
                "TTOO": val("Touroperador"),
                "MOTIVO LLAMADA": val("Motivo Urgencia"),
                "NOMBRE PACIENTE": val("Paciente"),
                "NHC A XANIT": val("Historia Medica"),
                "MEDICO DE URGENCIAS": val("Medico"),
                "OBSERVACIONES": val("Observaciones"),
                "MUNICIPIO": municipio,
                "ZONA AVISO": zona
            }
            export_data.append(row)
            
        try:
            df = pd.DataFrame(export_data)
            # Reorder columns to ensure exact sequence
            cols = ["FECHA", "TIPO EMISOR", "EMISOR", "HAB.", "TTOO", "MOTIVO LLAMADA", 
                    "NOMBRE PACIENTE", "NHC A XANIT", "MEDICO DE URGENCIAS", "OBSERVACIONES", 
                    "MUNICIPIO", "ZONA AVISO"]
            
            # Ensure all columns exist
            for col in cols:
                if col not in df.columns:
                    df[col] = ""
                    
            df = df[cols]
            
            if filename.endswith(".ods"):
                df.to_excel(filename, engine="odf", index=False)
            else:
                df.to_excel(filename, index=False)
                
            return True, "Exportación exitosa."
        except Exception as e:
            return False, str(e)

class MedicoManager:
    FILE_NAME = "medicos.csv"
    FIELDS = ["Nombre", "Telefono"]

    @classmethod
    def load_medicos(cls):
        if not os.path.isfile(cls.FILE_NAME):
            # Create default if not exists
            default_data = [
                {"Nombre": "Dr. Juan Pérez", "Telefono": "34600000001"},
                {"Nombre": "Dra. Ana Martínez", "Telefono": "34600000002"},
            ]
            cls.save_all(default_data)
            return default_data
            
        try:
            with open(cls.FILE_NAME, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                return list(reader)
        except Exception as e:
            print(f"Error loading Medicos: {e}")
            return []

    @classmethod
    def save_all(cls, medicos_list):
        try:
            with open(cls.FILE_NAME, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=cls.FIELDS)
                writer.writeheader()
                for m in medicos_list:
                    writer.writerow(m)
            return True, "Guardado."
        except Exception as e:
            return False, str(e)

    @classmethod
    def add_medico(cls, nombre, telefono):
        medicos = cls.load_medicos()
        medicos.append({"Nombre": nombre, "Telefono": telefono})
        return cls.save_all(medicos)

    @classmethod
    def delete_medico(cls, index):
        medicos = cls.load_medicos()
        if 0 <= index < len(medicos):
            del medicos[index]
            return cls.save_all(medicos)
        return False, "Índice no válido."

    @classmethod
    def get_phone(cls, nombre):
        medicos = cls.load_medicos()
        for m in medicos:
            if m["Nombre"] == nombre:
                return m.get("Telefono", "")
        return ""

class MedicosTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        
        # Left: List
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Nombre del Médico", "Teléfono (+34...)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)
        
        # Right: Controls
        ctrl_layout = QVBoxLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Nombre Dr/a...")
        ctrl_layout.addWidget(QLabel("NOMBRE:"))
        ctrl_layout.addWidget(self.name_edit)
        
        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("34600123456")
        ctrl_layout.addWidget(QLabel("TELÉFONO:"))
        ctrl_layout.addWidget(self.phone_edit)
        
        self.add_btn = QPushButton("AÑADIR MÉDICO")
        self.add_btn.clicked.connect(self.add_medico)
        ctrl_layout.addWidget(self.add_btn)
        
        self.del_btn = QPushButton("ELIMINAR SELECCIONADO")
        self.del_btn.setObjectName("DeleteBtn")
        self.del_btn.clicked.connect(self.delete_medico)
        ctrl_layout.addWidget(self.del_btn)
        
        ctrl_layout.addStretch()
        layout.addLayout(ctrl_layout)
        
        self.load_data()

    def load_data(self):
        self.table.setRowCount(0)
        medicos = MedicoManager.load_medicos()
        self.table.setRowCount(len(medicos))
        for i, m in enumerate(medicos):
            self.table.setItem(i, 0, QTableWidgetItem(m.get("Nombre", "")))
            self.table.setItem(i, 1, QTableWidgetItem(m.get("Telefono", "")))

    def add_medico(self):
        name = self.name_edit.text().strip()
        phone = self.phone_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "El nombre es obligatorio")
            return
        
        MedicoManager.add_medico(name, phone)
        self.name_edit.clear()
        self.phone_edit.clear()
        self.load_data()

    def delete_medico(self):
        row = self.table.currentRow()
        if row < 0:
            return
        
        name = self.table.item(row, 0).text()
        confirm = QMessageBox.question(self, "Confirmar", f"¿Eliminar a {name}?", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            MedicoManager.delete_medico(row)
            self.load_data()


class HotelManager:
    FILE_NAME = "hoteles.csv"
    FIELDS = ["Nombre"]

    @classmethod
    def load_hotels(cls):
        if not os.path.isfile(cls.FILE_NAME):
            # Create default with the huge list if not exists
            default_list = [
            "Hotel Claude (Marbella)", "Marbella Club Hotel", "Finca Cortesin (Casares)", "Hotel Puente Romano (Marbella)", 
            "Nobu Hotel Marbella", "Palacio Solecio (Malaga)", "Gran Hotel Miramar GL (Malaga)", "Hotel Don Pepe Gran Meliá (Marbella)", 
            "Mett Hotel & Beach Resort Marbella Estepona", "Vincci Selección Aleysa", "Eurostars Oasis Marbella", 
            "Casa la Concha (Marbella)", "Sea to Sky Suites (Mijas)", "Amanhavis Hotel (Benahavis)", "Hotel Carabeo", 
            "The Town House (Marbella)", "Room Mate Larios (Malaga)", "Molina Lario Hotel (Malaga)", "Catalonia Málaga", 
            "Hotel Well and Come Málaga", "Vincci Larios Diez (Malaga)", "H10 Croma Málaga", "Only YOU Hotel Málaga", 
            "Soho Boutique Equitativa (Malaga)", "Soho Boutique Las Vegas (Malaga)", "Ibis Budget Málaga Centro", 
            "Ibis Malaga Centro Ciudad", "Hotel Don Curro (Malaga)", "Mariposa Hotel Malaga", "Málaga Premium Hotel", 
            "Posada del Patio (Malaga)", "Hotel Riu Costa del Sol", "Hotel ILUNION Fuengirola", "Hotel IPV Palace & Spa", 
            "Hard Rock Hotel Marbella", "Melia Costa Del Sol", "Occidental Fuengirola", "Leonardo Hotel Fuengirola", 
            "Sol Torremolinos - Don Pablo", "Hotel Yaramar", "Hotel Angela", "Hotel Perla del Sur (Torremolinos)", 
            "Gran Marbella Resort & Beach Club", "Hotel Zen Airport", "Hotel Apartamentos Bajondillo (Torremolinos)", 
            "Holiday Inn Express Malaga Airport", "Hotel Goartín", "El Fuerte Marbella", "BYPILLOW California", 
            "Hotel Zeus", "Hotel Alay Puerto Marina", "Stay Unique Teatro Cervantes Street", "Hotel Lima", 
            "Hotel ILUNION Hacienda de Mijas", "Hotel Palacete de Álamos", "Don Carlos Marbella", "Wostel Malaga", 
            "Sol Guadalmar Hotel", "tent Torremolinos", "Hotel El Puerto by Pierre & Vacances", "THE FLAG Hotel Marbella", 
            "Occidental Puerto Banus", "Málaga Hotel Eliseos", "Hotel ILUNION Malaga", "Hotel Estepona Plaza", 
            "Hotel El Pilar Andalucia (Estepona)", "Travelodge Málaga Airport", "Hotel Sur Málaga", "Boutique Hotel Pueblo (Benalmadena)", 
            "Hotel La Casa (Torrox)", "Casa Diez (Estepona)", "Hotel Málaga Vibes", "Casa Consistorial (Fuengirola)", 
            "Gce Hoteles (Malaga)", "The Key Sensation Hotel (Torremolinos)", "Hotel Solymar (Malaga)", "MB Boutique Hotel (Nerja)", 
            "Soho Boutique Castillo de Santa Catalina", "Spirit Hotel Benalmadena Beach", "ME Marbella by Melia", 
            "Coral Beach Aparthotel", "Los Naranjos Singles", "Puerto Banus First Line"
            ]
            # Convert to list of dicts
            data = [{"Nombre": h} for h in default_list]
            cls.save_all(data)
            return data
            
        try:
            with open(cls.FILE_NAME, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                return list(reader)
        except Exception as e:
            print(f"Error loading Hotels: {e}")
            return []

    @classmethod
    def save_all(cls, hotels_list):
        try:
            with open(cls.FILE_NAME, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=cls.FIELDS)
                writer.writeheader()
                for h in hotels_list:
                    writer.writerow(h)
            return True, "Guardado."
        except Exception as e:
            return False, str(e)

    @classmethod
    def add_hotel(cls, nombre):
        hotels = cls.load_hotels()
        # Check duplicate
        if any(h["Nombre"].lower() == nombre.lower() for h in hotels):
             return False, "El hotel ya existe."
        
        hotels.append({"Nombre": nombre})
        # Sort alphabetically
        hotels.sort(key=lambda x: x["Nombre"])
        return cls.save_all(hotels)

    @classmethod
    def delete_hotel(cls, nombre):
        hotels = cls.load_hotels()
        hotels = [h for h in hotels if h["Nombre"] != nombre]
        return cls.save_all(hotels)

class HotelesTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        
        # Left: List
        self.table = QTableWidget()
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(["Nombre del Hotel"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self.on_hotel_selected)
        layout.addWidget(self.table)
        
        # Right: Controls + Map
        ctrl_layout = QVBoxLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Nombre del Hotel...")
        ctrl_layout.addWidget(QLabel("NUEVO HOTEL:"))
        ctrl_layout.addWidget(self.name_edit)
        
        self.add_btn = QPushButton("AÑADIR HOTEL")
        self.add_btn.clicked.connect(self.add_hotel)
        ctrl_layout.addWidget(self.add_btn)
        
        self.del_btn = QPushButton("ELIMINAR SELECCIONADO")
        self.del_btn.setObjectName("DeleteBtn")
        self.del_btn.clicked.connect(self.delete_hotel)
        ctrl_layout.addWidget(self.del_btn)
        
        # Add Google Maps viewer
        if WEBENGINE_AVAILABLE:
            map_label = QLabel("📍 UBICACIÓN EN MAPA:")
            map_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
            ctrl_layout.addWidget(map_label)
            
            self.map_view = QWebEngineView()
            self.map_view.setMinimumHeight(400)
            ctrl_layout.addWidget(self.map_view)
            
            # Load default map (centered on Costa del Sol)
            self.load_default_map()
        else:
            # If QWebEngineView is not available, show a message
            error_label = QLabel("⚠️ Visor de mapas no disponible.\nInstale PyQt6-WebEngine para ver mapas.")
            error_label.setStyleSheet("color: orange; padding: 10px;")
            ctrl_layout.addWidget(error_label)
            self.map_view = None
        
        ctrl_layout.addStretch()
        layout.addLayout(ctrl_layout)
        
        self.load_data()

    def load_default_map(self):
        """Load a default map centered on Costa del Sol using OpenStreetMap"""
        if not self.map_view:
            return
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <style>
                body, html { margin: 0; padding: 0; height: 100%; }
                #map { height: 100%; width: 100%; }
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script>
                // Initialize map centered on Costa del Sol
                var map = L.map('map').setView([36.5, -4.5], 10);
                
                // Add OpenStreetMap tiles
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '© OpenStreetMap contributors',
                    maxZoom: 19
                }).addTo(map);
            </script>
        </body>
        </html>
        """
        self.map_view.setHtml(html)

    def show_hotel_on_map(self, hotel_name):
        """Show the selected hotel on the map using Nominatim geocoding"""
        if not self.map_view or not hotel_name:
            return
        
        # Escape single quotes in hotel name for JavaScript
        safe_hotel_name = hotel_name.replace("'", "\\'")
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <style>
                body, html {{ margin: 0; padding: 0; height: 100%; }}
                #map {{ height: 100%; width: 100%; }}
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script>
                // Initialize map
                var map = L.map('map').setView([36.5, -4.5], 13);
                
                // Add OpenStreetMap tiles
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    attribution: '© OpenStreetMap contributors',
                    maxZoom: 19
                }}).addTo(map);
                
                // Geocode the hotel using Nominatim
                var hotelName = '{safe_hotel_name}';
                var searchQuery = encodeURIComponent(hotelName + ', Costa del Sol, España');
                
                fetch('https://nominatim.openstreetmap.org/search?format=json&q=' + searchQuery)
                    .then(response => response.json())
                    .then(data => {{
                        if (data && data.length > 0) {{
                            var lat = parseFloat(data[0].lat);
                            var lon = parseFloat(data[0].lon);
                            
                            // Center map on location
                            map.setView([lat, lon], 15);
                            
                            // Add marker
                            L.marker([lat, lon])
                                .addTo(map)
                                .bindPopup('<b>' + hotelName + '</b>')
                                .openPopup();
                        }} else {{
                            console.error('No se encontró la ubicación para: ' + hotelName);
                        }}
                    }})
                    .catch(error => {{
                        console.error('Error en geocodificación:', error);
                    }});
            </script>
        </body>
        </html>
        """
        self.map_view.setHtml(html)

    def on_hotel_selected(self):
        """Called when a hotel is selected in the table"""
        row = self.table.currentRow()
        if row >= 0:
            hotel_name = self.table.item(row, 0).text()
            self.show_hotel_on_map(hotel_name)

    def load_data(self):
        self.table.setRowCount(0)
        hotels = HotelManager.load_hotels()
        self.table.setRowCount(len(hotels))
        for i, h in enumerate(hotels):
            self.table.setItem(i, 0, QTableWidgetItem(h.get("Nombre", "")))

    def add_hotel(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "El nombre es obligatorio")
            return
        
        success, msg = HotelManager.add_hotel(name)
        if success:
            self.name_edit.clear()
            self.load_data()
        else:
            QMessageBox.warning(self, "Error", msg)

    def delete_hotel(self):
        row = self.table.currentRow()
        if row < 0:
            return
        
        name = self.table.item(row, 0).text()
        confirm = QMessageBox.question(self, "Confirmar", f"¿Eliminar {name}?", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            HotelManager.delete_hotel(name)
            self.load_data()
            if self.map_view:
                self.load_default_map()

class AvisoForm(QWidget):
    saved_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.edit_mode_index = -1
        
        main_layout = QVBoxLayout(self)
        
        # Container widget for the form
        self.form_widget = QWidget()
        self.grid = QGridLayout(self.form_widget)
        self.grid.setSpacing(10)
        self.grid.setHorizontalSpacing(0)
        self.grid.setContentsMargins(10, 10, 10, 10)
        
        main_layout.addWidget(self.form_widget)

        self._init_fields()

        # Define a list of all widgets that should be disabled when a notice is closed
        self.editable_widgets = [
            self.fecha_edit, self.emisor_cb, self.historia_edit, self.hotel_cb,
            self.habitacion_edit, self.paciente_edit, self.edad_spin,
            self.nacionalidad_cb, self.hora_solicitud_edit, self.motivo_edit,
            self.pagador_cb, self.touroperador_edit, self.seguro_edit,
            self.hora_avisos_edit, self.hora_fin_edit, self.medico_edit,
            self.diagnostico_edit, self.traslado_chk,
            self.observaciones_edit
        ]
        # Connect the status dropdown to the logic that enables/disables fields
        self.estado_cb.currentTextChanged.connect(self._on_status_changed)
        
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("GUARDAR AVISO")
        self.save_btn.clicked.connect(self.save)
        
        self.cancel_btn = QPushButton("CANCELAR EDICIÓN")
        self.cancel_btn.setObjectName("DeleteBtn")
        self.cancel_btn.setVisible(False)
        self.cancel_btn.clicked.connect(self.reset_form)

        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        main_layout.addLayout(btn_layout)
        
        # --- Pulse Animation for Save Button ---
        self.shadow_effect = QGraphicsDropShadowEffect(self.save_btn)
        self.shadow_effect.setBlurRadius(20)
        self.shadow_effect.setColor(QColor("#007acc"))
        self.shadow_effect.setOffset(0, 0)
        self.save_btn.setGraphicsEffect(self.shadow_effect)

        self.anim = QPropertyAnimation(self.shadow_effect, b"blurRadius")
        self.anim.setDuration(1500)
        self.anim.setStartValue(5)
        self.anim.setEndValue(30)
        self.anim.setEasingCurve(QEasingCurve.Type.SineCurve)
        self.anim.setLoopCount(-1) # Infinite loop
        self.anim.start()

        self.reset_form()

    def _init_fields(self):
        # --- HEADER: DATOS GENERALES ---
        # --- HEADER: DATOS GENERALES ---
        lbl_general = QLabel("DATOS GENERALES")
        lbl_general.setObjectName("HeaderLabel")
        # lbl_general.setStyleSheet(...) MOVED TO GLOBAL CSS
        self.grid.addWidget(lbl_general, 0, 0, 1, 6)  # Deja dos últimas columnas para ESTADO

        # --- Row 1: Fecha | Emisor | Estado ---
        self.grid.addWidget(QLabel("FECHA:"), 1, 0, alignment=Qt.AlignmentFlag.AlignRight)
        self.fecha_edit = QDateEdit(QDate.currentDate())
        self.fecha_edit.setCalendarPopup(True)
        self.grid.addWidget(self.fecha_edit, 1, 1)

        self.grid.addWidget(QLabel("EMISOR:"), 1, 4, alignment=Qt.AlignmentFlag.AlignRight)
        self.emisor_cb = QComboBox()
        self.emisor_cb.addItems(["Jaime", "Guia", "Paciente", "Seguro", "SMCS", "VITHAS", "RECEPCION", "GP"])
        self.emisor_cb.currentTextChanged.connect(self.on_emisor_changed)
        self.emisor_cb.setMaximumWidth(150)
        self.grid.addWidget(self.emisor_cb, 1, 5)

        # Mover ESTADO a la fila del encabezado (extremo derecho) con etiqueta encima y más ancho
        # Mover ESTADO a la fila del encabezado (extremo derecho) con etiqueta encima y más ancho
        self.estado_lbl = QLabel("ESTADO:")
        self.estado_lbl.setObjectName("EstadoLabel")
        # self.estado_lbl.setStyleSheet(...) MOVED TO GLOBAL CSS

        self.estado_cb = QComboBox()
        self.estado_cb.addItems(["Abierto", "Anulado", "Cerrado"])
        self.estado_cb.setObjectName("EstadoCombo")
        # StyleSheet moved to global CSS
        self.estado_cb.setMinimumWidth(220)
        self.estado_cb.setMinimumHeight(36)

        # Contenedor horizontal: etiqueta a la izquierda y combo a la derecha
        self.estado_container = QWidget()
        _estado_h = QHBoxLayout(self.estado_container)
        _estado_h.setContentsMargins(0, 0, 0, 0)
        _estado_h.setSpacing(8)
        _estado_h.addWidget(self.estado_lbl)
        _estado_h.addWidget(self.estado_cb)
        _estado_h.addStretch(0)

        # Colocar en la esquina superior derecha ocupando 2 columnas
        self.grid.addWidget(self.estado_container, 0, 6, 1, 2, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        # NHC debajo del Estado, alineado verticalmente
        self.lbl_nhc = QLabel("NHC:")
        self.lbl_nhc.setObjectName("EstadoLabel")  # Usar el mismo estilo que Estado para consistencia
        self.historia_edit = QLineEdit()
        self.historia_edit.setPlaceholderText("Nº Historia")
        self.historia_edit.setMinimumWidth(220)
        self.historia_edit.setMinimumHeight(36)
        
        # Contenedor para NHC (similar al de Estado)
        self.nhc_container = QWidget()
        _nhc_h = QHBoxLayout(self.nhc_container)
        _nhc_h.setContentsMargins(0, 0, 0, 0)
        _nhc_h.setSpacing(8)
        _nhc_h.addWidget(self.lbl_nhc)
        _nhc_h.addWidget(self.historia_edit)
        _nhc_h.addStretch(0)
        
        # Colocar debajo del Estado, alineado a la derecha
        self.grid.addWidget(self.nhc_container, 1, 6, 1, 2, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        # --- Row 2: Hotel | Paciente | Edad | NHC ---
        # Note: Added Paciente here to keep it visible and logical
        self.lbl_hotel = QLabel("HOTEL:")
        self.grid.addWidget(self.lbl_hotel, 2, 0, alignment=Qt.AlignmentFlag.AlignRight)
        self.hotel_cb = QComboBox()
        self.hotel_cb.setEditable(True)
        # Populate hotels
        self._reload_hotels()
        # Place HOTEL and HABITACIÓN adjacent: hotel spans 2 cols, habitacion next to it
        self.grid.addWidget(self.hotel_cb, 2, 1, 1, 2)

        # HABITACIÓN: alineado con EMISOR y EDAD en columna 5
        self.grid.addWidget(QLabel("HABITACIÓN:"), 2, 4, alignment=Qt.AlignmentFlag.AlignRight)
        self.habitacion_edit = QLineEdit()
        self.habitacion_edit.setMaximumWidth(150)
        self.grid.addWidget(self.habitacion_edit, 2, 5)

        # DISTANCIA debajo del NHC, alineado verticalmente a la derecha
        self.lbl_distancia = QLabel("DISTANCIA (km):")
        # Usar estilo normal de etiqueta (no EstadoLabel)
        self.distancia_edit = QLineEdit()
        self.distancia_edit.setReadOnly(True)
        self.distancia_edit.setMinimumWidth(220)
        self.distancia_edit.setMinimumHeight(36)
        self.distancia_edit.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Contenedor para DISTANCIA (similar al de Estado y NHC)
        self.distancia_container = QWidget()
        _distancia_h = QHBoxLayout(self.distancia_container)
        _distancia_h.setContentsMargins(0, 0, 0, 0)
        _distancia_h.setSpacing(8)
        _distancia_h.addWidget(self.lbl_distancia)
        _distancia_h.addWidget(self.distancia_edit)
        _distancia_h.addStretch(0)
        
        # Colocar debajo del NHC, alineado a la derecha
        self.grid.addWidget(self.distancia_container, 2, 6, 1, 2, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        # Recompute distancia when hotel selection changes
        self.hotel_cb.currentTextChanged.connect(self.update_distancia)
        
        # --- Row 3: Paciente (3 cols) | Edad (1 col) | Nacionalidad (1 col) ---
        self.grid.addWidget(QLabel("PACIENTE:"), 3, 0, alignment=Qt.AlignmentFlag.AlignRight)
        self.paciente_edit = QLineEdit()
        self.grid.addWidget(self.paciente_edit, 3, 1, 1, 3) # Spans 3 cols

        # EDAD: crear contenedor para juntar etiqueta y valor
        lbl_edad = QLabel("EDAD:")
        self.edad_spin = QSpinBox()
        self.edad_spin.setRange(0, 120)
        self.edad_spin.setMaximumWidth(70)  # Ancho reducido para 3 dígitos
        
        # Contenedor horizontal para EDAD
        edad_container = QWidget()
        edad_layout = QHBoxLayout(edad_container)
        edad_layout.setContentsMargins(0, 0, 0, 0)
        edad_layout.setSpacing(5)
        edad_layout.addWidget(lbl_edad)
        edad_layout.addWidget(self.edad_spin)
        edad_layout.addStretch()
        
        self.grid.addWidget(edad_container, 3, 4, 1, 2, alignment=Qt.AlignmentFlag.AlignRight)

        # NACIONALIDAD debajo de DISTANCIA, alineado verticalmente a la derecha
        self.lbl_nacionalidad = QLabel("NACIONALIDAD:")
        # Usar estilo normal de etiqueta (no EstadoLabel)
        self.nacionalidad_cb = QComboBox()
        self.nacionalidad_cb.setEditable(True)
        self.nacionalidad_cb.setMinimumWidth(220)
        self.nacionalidad_cb.setMinimumHeight(36)
        self.nacionalidad_cb.addItems([
            "Español/a", "Británico/a", "Francés/a", "Alemán/a", "Italiano/a", "Holandés/a", "Belga", "Portugués/a", 
            "Sueco/a", "Noruego/a", "Danés/a", "Finlandés/a", "Irlandés/a", "Suizo/a", "Austríaco/a", "Polaco/a", 
            "Rumano/a", "Búlgaro/a", "Ucraniano/a", "Ruso/a", "Checo/a", "Eslovaco/a", "Húngaro/a", "Griego/a", 
            "Croata", "Serbio/a", "Bosnio/a", "Albanés/a", "Turco/a", "Marroquí", "Argelino/a", "Tunecino/a", 
            "Egipcio/a", "Chino/a", "Japonés/a", "Indio/a", "Pakistaní", "Estadounidense", "Canadiense", "Mexicano/a", 
            "Brasileño/a", "Argentino/a", "Colombiano/a", "Chileno/a", "Peruano/a", "Venezolano/a", "Ecuatoriano/a", 
            "Uruguayo/a", "Paraguayo/a", "Boliviano/a", "Cubano/a", "Dominicano/a", "Australiano/a", "Neozelandés/a",
            "Afgano/a", "Andorrano/a", "Angoleño/a", "Árabe", "Armenio/a", "Azerbaiyano/a", "Bangladesí", 
            "Beliceño/a", "Bielorruso/a", "Birmano/a", "Camerunés/a", "Catarí", "Coreano/a", "Costarricense", 
            "Chipriota", "Emiratí", "Esloveno/a", "Estonio/a", "Etíope", "Filipino/a", "Georgiano/a", "Ghanés/a", 
            "Guatemalteco/a", "Hondureño/a", "Indonesio/a", "Iraquí", "Iraní", "Islandés/a", "Israelí", 
            "Jamaicano/a", "Jordano/a", "Kazajo/a", "Keniano/a", "Kuwaití", "Letón/a", "Libanés/a", "Lituano/a", 
            "Luxemburgués/a", "Macedonio/a", "Malayo/a", "Maltés/a", "Mongol/a", "Nigeriano/a", "Panameño/a", 
            "Salvadoreño/a", "Saudi", "Senegalés/a", "Singapurense", "Sirio/a", "Somalí", "Sudafricano/a", 
            "Tailandés/a", "Vietnamita", "Yemení"
        ])
        
        # Contenedor para NACIONALIDAD (similar al de Estado, NHC y Distancia)
        self.nacionalidad_container = QWidget()
        _nacionalidad_h = QHBoxLayout(self.nacionalidad_container)
        _nacionalidad_h.setContentsMargins(0, 0, 0, 0)
        _nacionalidad_h.setSpacing(8)
        _nacionalidad_h.addWidget(self.lbl_nacionalidad)
        _nacionalidad_h.addWidget(self.nacionalidad_cb)
        _nacionalidad_h.addStretch(0)
        
        # Colocar debajo de DISTANCIA, alineado a la derecha
        self.grid.addWidget(self.nacionalidad_container, 3, 6, 1, 2, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        # --- Row 4: Hora Llamada | Motivo ---
        self.grid.addWidget(QLabel("HORA LLAMADA:"), 4, 0, alignment=Qt.AlignmentFlag.AlignRight)
        self.hora_solicitud_edit = QTimeEdit(QTime.currentTime())
        self.grid.addWidget(self.hora_solicitud_edit, 4, 1) # Moved to col 1
        
        self.grid.addWidget(QLabel("MOTIVO:"), 4, 2, alignment=Qt.AlignmentFlag.AlignRight)
        self.motivo_edit = QLineEdit()
        self.grid.addWidget(self.motivo_edit, 4, 3, 1, 5) # Spans rest (3 to 7 = 5 cols)

        # Row 5 continued
        self.grid.addWidget(QLabel("PAGADOR:"), 5, 0, alignment=Qt.AlignmentFlag.AlignRight)
        self.pagador_cb = QComboBox()
        self.pagador_cb.addItems(["Paciente", "Seguro", "Hotel"])
        self.pagador_cb.currentTextChanged.connect(self.toggle_seguro_field)
        self.grid.addWidget(self.pagador_cb, 5, 1)

        # Define Touroperador fields First
        self.lbl_touroperador = QLabel("TOUROPERADOR:")
        self.touroperador_edit = QComboBox()
        self.touroperador_edit.setEditable(True)
        self.touroperador_edit.addItems([
            "TUI", "Jet2Holidays", "Vueling Holidays", "Booking.com", "Expedia", "Alltours", 
            "FTI Touristik", "Der Touristik", "Schauinsland Reisen", "Luxair Tours", "Soltour", 
            "Bravo Tour Plus", "Euroclass", "Feeltravel", "Monturista", "Newtourvis", "Solfie", 
            "Bespoke Travel", "Galeota Tourism", "TOMA & COE", "Julià Travel", "Marina Sun Travel", 
            "Abies Travel", "Al Andalus Travel", "Andalucia Auténtica"
        ])
        
        # Define Seguro fields Second (used later)
        self.lbl_seguro = QLabel("SEGURO:")
        
        self.seguro_edit = QComboBox()
        self.seguro_edit.setEditable(True)
        self.seguro_edit.addItems([
            "Falck TravelCare", "SOS International", "Allianz Global Assistance", "AXA Global Healthcare", 
            "Cigna Global", "Bupa Global", "Aetna International", "UnitedHealthcare Global", 
            "Seven Corners", "IMG (International Medical Group)", "GeoBlue", "WorldTrips", 
            "Tokio Marine HCC", "Hiscox", "Mapfre", "Generali Global Assistance", 
            "MSH International", "April International", "Foyer Global Health", "Now Health International", 
            "William Russell", "Integra Global", "Morgan Price", "Globality Health", 
            "Henner", "DKV", "Sanitas", "Best Doctors", "Vumi", "Blue Cross Blue Shield Global"
        ])
        self.seguro_edit.setVisible(False)
        self.lbl_seguro.setVisible(False)

        # Add to Grid in Correct Order: Pagador (already added) -> TTOO -> Seguro
        self.grid.addWidget(self.lbl_touroperador, 5, 2, alignment=Qt.AlignmentFlag.AlignRight)
        self.grid.addWidget(self.touroperador_edit, 5, 3)
        
        self.grid.addWidget(self.lbl_seguro, 5, 4, alignment=Qt.AlignmentFlag.AlignRight)
        self.grid.addWidget(self.seguro_edit, 5, 5, 1, 3)

        # --- SEPARATOR ---
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        self.grid.addWidget(line, 6, 0, 1, 8)

        # --- HEADER: DATOS MEDICOS ---
        # --- HEADER: DATOS MEDICOS ---
        lbl_medico = QLabel("DATOS MÉDICOS")
        lbl_medico.setObjectName("HeaderLabel")
        # lbl_medico.setStyleSheet(...) MOVED TO GLOBAL CSS
        self.grid.addWidget(lbl_medico, 7, 0, 1, 8)

        # --- Row 8: Hora Avisos ---
        self.grid.addWidget(QLabel("HORA AVISOS:"), 8, 0, alignment=Qt.AlignmentFlag.AlignRight)
        self.hora_avisos_edit = QTimeEdit(QTime.currentTime())
        self.grid.addWidget(self.hora_avisos_edit, 8, 1)
        
        self.grid.addWidget(QLabel("HORA FIN:"), 8, 2, alignment=Qt.AlignmentFlag.AlignRight)
        self.hora_fin_edit = QTimeEdit(QTime.currentTime())
        self.grid.addWidget(self.hora_fin_edit, 8, 3)

        # --- Row 9: Medico | Telefono | Diagnostico ---
        self.grid.addWidget(QLabel("MÉDICO:"), 9, 0, alignment=Qt.AlignmentFlag.AlignRight)
        # Médico + Teléfono juntos para máxima legibilidad
        self.medico_edit = QComboBox()
        self.medico_edit.setEditable(True)
        self.medico_edit.currentTextChanged.connect(self.update_medico_phone)

        self.telefono_medico_edit = QLineEdit()
        self.telefono_medico_edit.setReadOnly(True)
        self.telefono_medico_edit.setMaximumWidth(140)
        self.telefono_medico_edit.setPlaceholderText("TEL")
        self.telefono_medico_edit.setStyleSheet("""
            QLineEdit {
                background: transparent;
                color: #00f3ff;
                border: none;
                padding: 0;
                margin: 0;
            }
        """)
        self.telefono_medico_edit.setFrame(False)

        # Colocar los campos en la cuadrícula para alinear TELÉFONO con HORA FIN y TIPO TRASLADO
        # MÉDICO en columna 1
        self.grid.addWidget(self.medico_edit, 9, 1)
        # Etiqueta TELÉFONO en columna 2 (alineada a la derecha como las demás)
        tel_label = QLabel("TELÉFONO:")
        self.grid.addWidget(tel_label, 9, 2, alignment=Qt.AlignmentFlag.AlignRight)
        # Valor de TELÉFONO en columna 3 (misma columna que HORA FIN / TIPO TRASLADO)
        self.grid.addWidget(self.telefono_medico_edit, 9, 3)

        self.grid.addWidget(QLabel("DIAGNÓSTICO:"), 9, 4, alignment=Qt.AlignmentFlag.AlignRight)
        self.diagnostico_edit = QLineEdit()
        self.grid.addWidget(self.diagnostico_edit, 9, 5, 1, 3)
        
        # --- Row 10: Traslado ---
        self.traslado_chk = QCheckBox(" REQUIERE TRASLADO") 
        self.traslado_chk.setCursor(Qt.CursorShape.PointingHandCursor)
        self.traslado_chk.setObjectName("TrasladoCheck")
        # StyleSheet moved to global CSS
        self.traslado_chk.stateChanged.connect(self.toggle_traslado)
        self.grid.addWidget(QLabel("TRASLADO:"), 10, 0, alignment=Qt.AlignmentFlag.AlignRight)
        self.grid.addWidget(self.traslado_chk, 10, 1)

        self.lbl_tipo_traslado = QLabel("TIPO TRASLADO:")
        self.grid.addWidget(self.lbl_tipo_traslado, 10, 2, alignment=Qt.AlignmentFlag.AlignRight)
        self.tipo_traslado_cb = QComboBox()
        self.tipo_traslado_cb.addItems(["Ambulancias Andalucia", "Ambulancias AGP", "Helicopteros Sanitarios", "Medios Propios"])
        self.tipo_traslado_cb.setEnabled(False)
        self.tipo_traslado_cb.currentTextChanged.connect(self.toggle_ambulancia)
        self.grid.addWidget(self.tipo_traslado_cb, 10, 3)

        self.lbl_hora_ambulancia = QLabel("HORA AMB.:")
        self.grid.addWidget(self.lbl_hora_ambulancia, 10, 4, alignment=Qt.AlignmentFlag.AlignRight)
        self.hora_ambulancia_edit = QTimeEdit(QTime.currentTime())
        self.hora_ambulancia_edit.setEnabled(False)
        self.grid.addWidget(self.hora_ambulancia_edit, 10, 5)

        # --- Row 11: Ingreso ---
        self.grid.addWidget(QLabel("INGRESO:"), 11, 0, alignment=Qt.AlignmentFlag.AlignRight)
        self.ingreso_cb = QComboBox()
        self.ingreso_cb.addItems(["No ingresa", "Planta", "UCI"])
        self.grid.addWidget(self.ingreso_cb, 11, 1)

        self.grid.addWidget(QLabel("MÉDICO INGRESO:"), 11, 2, alignment=Qt.AlignmentFlag.AlignRight)
        self.medico_ingreso_cb = QComboBox()
        self.medico_ingreso_cb.setEditable(True)
        self.grid.addWidget(self.medico_ingreso_cb, 11, 3, 1, 3)

        self.refresh_doctors()

        # Initialize state based on checkbox (default unchecked)
        self.toggle_traslado()

        # --- Row 12: Observaciones ---
        self.grid.addWidget(QLabel("OBSERVACIONES:"), 12, 0, alignment=Qt.AlignmentFlag.AlignRight)
        self.observaciones_edit = QTextEdit()
        self.observaciones_edit.setMaximumHeight(80)
        self.grid.addWidget(self.observaciones_edit, 12, 1, 1, 7)

    def on_emisor_changed(self, text):
        # Logic for GP -> Change Hotel Layout
        if text == "GP":
            self.lbl_hotel.setText("GP:")
            self.hotel_cb.clear() 
            self.hotel_cb.addItems(["DR. LANDMAN", "DR. BUSTER", "DR. WIKLUND", "CLINICA LA CALA", "OTRO"])
        elif text == "VITHAS":
            self.lbl_hotel.setText("HOSPITAL:")
            self.hotel_cb.clear()
            self.hotel_cb.addItems(["VITHAS NERJA", "VITHAS MALAGA", "VITHAS BENALMADENA", "VITHAS ESTEPONA"])
        else:
            self.lbl_hotel.setText("HOTEL:")
            # Force reload of hotels when switching back from GP or any mode
            self.hotel_cb.clear()
            self._reload_hotels()

        # Fix: Ensure no hotel is pre-selected by default for ANY emisor type
        self.hotel_cb.setCurrentIndex(-1)
        self.hotel_cb.setEditText("")

    def toggle_seguro_field(self, text):
        is_seguro = (text == "Seguro")
        
        self.lbl_seguro.setVisible(is_seguro)
        self.seguro_edit.setVisible(is_seguro)
        
        if is_seguro:
            # Layout: Pagador | Seguro | Touroperador
            # Move SEGURO to Col 2-3
            self.grid.addWidget(self.lbl_seguro, 5, 2, alignment=Qt.AlignmentFlag.AlignRight)
            self.grid.addWidget(self.seguro_edit, 5, 3)
            
            # Move TTOO to Col 4-5
            self.grid.addWidget(self.lbl_touroperador, 5, 4, alignment=Qt.AlignmentFlag.AlignRight)
            self.grid.addWidget(self.touroperador_edit, 5, 5, 1, 3)
            
        else:
            self.seguro_edit.setCurrentIndex(-1)
            # Layout: Pagador | Touroperador | (Seguro Hidden)
            # Move TTOO back to Col 2-3
            self.grid.addWidget(self.lbl_touroperador, 5, 2, alignment=Qt.AlignmentFlag.AlignRight)
            self.grid.addWidget(self.touroperador_edit, 5, 3)
            
            # Put Seguro in 4-5 just to keep it somewhere valid (though hidden)
            self.grid.addWidget(self.lbl_seguro, 5, 4, alignment=Qt.AlignmentFlag.AlignRight)
            self.grid.addWidget(self.seguro_edit, 5, 5, 1, 3)

    def refresh_hotels(self):
        self._reload_hotels()

    def _reload_hotels(self):
        self.hotel_cb.clear()
        hotels = HotelManager.load_hotels()
        # Fallback if empty (first run before manager saves default?)
        # Manager logic handles default creation, so we just check if it returned anything
        if not hotels:
            # Just in case something failed catastrophically, keep a minimal list or empty
             self.hotel_cb.addItems(["Hotel Claude (Marbella)"])
        else:
            self.hotel_cb.addItems([h["Nombre"] for h in hotels])
            
        # FORCE EMPTY INITIAL STATE:
        self.hotel_cb.setCurrentIndex(-1)
        self.hotel_cb.setEditText("")
        if hasattr(self.hotel_cb, "lineEdit") and self.hotel_cb.lineEdit():
            self.hotel_cb.lineEdit().clear()

    def update_distancia(self, hotel_name: str):
        """Calculate approximate distance (km) between selected hotel (by municipio)
        and Vithas Xanit. Uses Municipio resolved by HotelLocationManager and falls
        back to 'PENDIENTE' -> shows 'N/A' when unknown.
        """
        if not hotel_name:
            self.distancia_edit.setText("")
            return

        # First try a cached or geocoded exact hotel coordinate (better precision)
        cache = load_coords_cache()
        coord = None
        key = hotel_name.strip()
        if key in cache:
            c = cache[key]
            coord = (float(c["lat"]), float(c["lon"]))
        else:
            # Try geocoding the hotel name online (Nominatim)
            geo = geocode_hotel(hotel_name)
            if geo:
                coord = geo
                # store to cache
                try:
                    cache[key] = {"lat": coord[0], "lon": coord[1]}
                    save_coords_cache(cache)
                except Exception:
                    pass

        # If still no exact coord, fall back to municipio approximate coord
        if coord is None:
            municipio, zona = HotelLocationManager.get_location(hotel_name)
            # Try exact municipio key
            if municipio in MUNICIPIO_COORDS:
                coord = MUNICIPIO_COORDS[municipio]
            else:
                for mkey in MUNICIPIO_COORDS:
                    if mkey.lower() in municipio.lower() or municipio.lower() in mkey.lower():
                        coord = MUNICIPIO_COORDS[mkey]
                        break

        if coord is None:
            self.distancia_edit.setText("N/A")
            return

        dist = haversine_km(coord, HOSPITAL_XANIT_COORD)
        self.distancia_edit.setText(f"{dist:.1f}")

    def toggle_traslado(self):
        checked = self.traslado_chk.isChecked()
        
        # List of widgets to enable/disable
        widgets = [self.tipo_traslado_cb, self.ingreso_cb, self.medico_ingreso_cb]
        
        # Specific blue style for disabled state (User Request)
        # Normal style is handled by global stylesheet, so we clear it when enabled.
        disabled_style = """
            opacity: 0.7;
            background-color: rgba(0, 85, 164, 0.2); 
            color: #0088cc; 
            border: 1px solid #005577;
        """
        
        for w in widgets:
            w.setEnabled(checked)
            if not checked:
                w.setStyleSheet(disabled_style)
            else:
                w.setStyleSheet("") # Revert to global theme
                
        # Handle Hora Ambulancia separately as it has extra logic
        if not checked: 
            self.hora_ambulancia_edit.setEnabled(False)
            self.hora_ambulancia_edit.setStyleSheet(disabled_style)
        else:
            # Re-evaluate based on type logic
            self.toggle_ambulancia(self.tipo_traslado_cb.currentText())

    def toggle_ambulancia(self, text):
        # Only touch this if Traslado is actually checked. 
        # If Traslado is unchecked, the main toggle_traslado handles disabling everything.
        if not self.traslado_chk.isChecked():
            return

        text_lower = text.lower()
        # Enable if ambulance or helicopter is selected
        if "ambulancia" in text_lower or "helicoptero" in text_lower:
            self.hora_ambulancia_edit.setEnabled(True)
            self.hora_ambulancia_edit.setStyleSheet("") # Revert to global
        else:
            self.hora_ambulancia_edit.setEnabled(False)
            # Apply the blue disabled style here too for consistency if needed
            self.hora_ambulancia_edit.setStyleSheet("""
                opacity: 0.7;
                background-color: rgba(0, 85, 164, 0.2); 
                color: #0088cc; 
                border: 1px solid #005577;
            """)

    def update_medico_phone(self, text):
        phone = MedicoManager.get_phone(text)
        self.telefono_medico_edit.setText(phone)
        
        if phone:
            # User requested "MUY CLARO, COLOR LLAMATIVO"
            self.telefono_medico_edit.setStyleSheet("""
                QLineEdit { 
                    background-color: #ccff00; 
                    color: #000000; 
                    font-weight: bold; 
                    font-size: 14px;
                    border: 2px solid #ccff00;
                    border-radius: 4px;
                }
            """)
        else:
            # Revert to disabled/subtle style
            self.telefono_medico_edit.setStyleSheet("""
                QLineEdit { 
                    background-color: rgba(0, 0, 0, 0.1); 
                    color: #555; 
                    border: 1px dotted #888;
                }
            """)

    def _set_fields_editable(self, editable):
        """Enable or disable all form fields, except for the 'Estado' dropdown."""
        # For text-based widgets, setReadOnly allows users to still copy text.
        # For interactive widgets like combos/checkboxes, setEnabled is more appropriate.
        for widget in self.editable_widgets:
            if isinstance(widget, (QLineEdit, QTextEdit, QSpinBox, QDateEdit, QTimeEdit)):
                widget.setReadOnly(not editable)
            elif isinstance(widget, (QComboBox, QCheckBox)):
                widget.setEnabled(editable)

        # The 'save' button should also be enabled/disabled.
        # self.save_btn.setEnabled(editable) # DISABLED: Always allow saving to permit closing notices

        # If we are enabling fields, we must re-evaluate custom UI logic 
        # that might have been disabled (e.g., for traslado, seguro).
        if editable:
            self.toggle_seguro_field(self.pagador_cb.currentText())
            self.toggle_traslado()
        # If disabling, the loop has already disabled traslado-dependent fields if they are in the list.
        # We need to make sure the specific ones controlled by toggles are also off.
        else:
            self.tipo_traslado_cb.setEnabled(False)
            self.hora_ambulancia_edit.setEnabled(False)
            self.ingreso_cb.setEnabled(False)
            self.medico_ingreso_cb.setEnabled(False)

    def _on_status_changed(self, status, is_initial_load=False):
        """Handles logic when the 'Estado' of the notice changes."""
        is_closed = (status == "Cerrado")
        
        # Only lock fields if it's the initial load of a closed notice.
        # If the user is manually changing to 'Cerrado', we keep fields editable 
        # so they can finish edits and save.
        if is_initial_load:
             self._set_fields_editable(not is_closed)
        else:
            # If manually changing:
            # - If switching TO Abierto/Anulado: Unlock fields
            # - If switching TO Cerrado: Do NOT lock fields immediately
            if not is_closed:
                self._set_fields_editable(True)

    def load_aviso_for_editing(self, index, data):
        self.edit_mode_index = index
        self.save_btn.setText("ACTUALIZAR DATOS")
        self.cancel_btn.setVisible(True)

        # --- CRITICAL SECTION: Block all signals to control population order ---
        self.emisor_cb.blockSignals(True)
        self.hotel_cb.blockSignals(True)
        self.pagador_cb.blockSignals(True)
        self.traslado_chk.blockSignals(True)
        self.tipo_traslado_cb.blockSignals(True)
        self.medico_edit.blockSignals(True)
        self.estado_cb.blockSignals(True) # Block status signal during load

        # --- SET ALL VALUES FROM DATA ---
        
        # 1. Set emisor, which dictates the hotel list
        emisor = data.get("Emisor", "")
        self.emisor_cb.setCurrentText(emisor)
        
        # 2. Manually populate hotel list based on the emisor
        self.on_emisor_changed(emisor) 
        
        # 3. NOW set the correct hotel from the data (with robust, case-insensitive matching)
        raw_hotel = data.get("Hotel")
        hotel_to_set = str(raw_hotel).strip() if raw_hotel else ""
        
        # Perform a case-insensitive search for the hotel in the combobox items.
        found_index = -1
        if hotel_to_set: 
            for i in range(self.hotel_cb.count()):
                item_text = self.hotel_cb.itemText(i).strip()
                if item_text.lower() == hotel_to_set.lower():
                    found_index = i
                    break
        
        if found_index >= 0:
            # If a match is found in the list, set the combobox to that index.
            self.hotel_cb.setCurrentIndex(found_index)
        else:
            # If no match is found, force the text into the line edit directly.
            # This bypasses any ambiguity with setCurrentText/Index on editable combos.
            self.hotel_cb.setCurrentIndex(-1)
            self.hotel_cb.setEditText(hotel_to_set)

        # Set the rest of the fields
        self.hora_solicitud_edit.setTime(QTime.fromString(data.get("Hora Solicitud", "00:00"), "HH:mm"))
        self.fecha_edit.setDate(QDate.fromString(data.get("Fecha", ""), "yyyy-MM-dd"))
        self.habitacion_edit.setText(data.get("Habitacion") or "")
        self.estado_cb.setCurrentText(data.get("Estado"))
        self.paciente_edit.setText(data.get("Paciente"))
        self.edad_spin.setValue(int(data.get("Edad") or 0))
        self.historia_edit.setText(data.get("Historia Medica"))
        self.nacionalidad_cb.setCurrentText(data.get("Nacionalidad"))
        self.motivo_edit.setText(data.get("Motivo Urgencia"))
        self.pagador_cb.setCurrentText(data.get("Pagador"))
        self.seguro_edit.setCurrentText(data.get("Seguro"))
        self.touroperador_edit.setCurrentText(data.get("Touroperador"))
        self.hora_avisos_edit.setTime(QTime.fromString(data.get("Hora Avisos", "00:00"), "HH:mm"))
        self.hora_fin_edit.setTime(QTime.fromString(data.get("Hora Finalizacion", "00:00"), "HH:mm"))
        self.medico_edit.setCurrentText(data.get("Medico"))
        self.diagnostico_edit.setText(data.get("Diagnostico"))
        self.traslado_chk.setChecked(data.get("Traslado") == "Si")
        self.tipo_traslado_cb.setCurrentText(data.get("Tipo Traslado"))
        self.hora_ambulancia_edit.setTime(QTime.fromString(data.get("Hora Ambulancia", "00:00"), "HH:mm"))
        self.ingreso_cb.setCurrentText(data.get("Ingreso"))
        self.medico_ingreso_cb.setCurrentText(data.get("Medico Ingreso"))
        self.observaciones_edit.setText(data.get("Observaciones"))

        # --- UNBLOCK AND MANUALLY UPDATE UI ---
        self.emisor_cb.blockSignals(False)
        self.hotel_cb.blockSignals(False)
        self.pagador_cb.blockSignals(False)
        self.traslado_chk.blockSignals(False)
        self.tipo_traslado_cb.blockSignals(False)
        self.medico_edit.blockSignals(False)
        self.estado_cb.blockSignals(False) # Unblock status signal
        
        # Manually trigger all UI updates that depend on the loaded data
        self.toggle_seguro_field(self.pagador_cb.currentText())
        self.toggle_traslado() # This will also handle the dependent ambulancia field
        self.update_distancia(self.hotel_cb.currentText())
        self.update_medico_phone(self.medico_edit.currentText())

        # Set the initial locked/unlocked state based on the loaded status.
        # This must be LAST, after all other UI state has been set.
        self._on_status_changed(self.estado_cb.currentText(), is_initial_load=True)

    def reset_form(self):
        self.edit_mode_index = -1
        self.save_btn.setText("GUARDAR AVISO")
        self.cancel_btn.setVisible(False)
        
        # Clear specific fields
        if hasattr(self, 'distancia_edit'):
            self.distancia_edit.clear()
        
        self.habitacion_edit.clear()
        self.paciente_edit.clear()
        self.edad_spin.setValue(0)
        self.historia_edit.clear()
        self.nacionalidad_cb.setCurrentIndex(-1)
        self.motivo_edit.clear()
        self.touroperador_edit.setCurrentIndex(-1)
        self.medico_edit.setCurrentIndex(-1)
        self.diagnostico_edit.clear()
        self.traslado_chk.setChecked(False)
        self.ingreso_cb.setCurrentIndex(-1)
        self.medico_ingreso_cb.setCurrentIndex(-1)
        self.observaciones_edit.clear()
        self.seguro_edit.setCurrentIndex(-1)
        
        # Reset combos to defaults
        self.estado_cb.setCurrentIndex(0) # Pendiente/Abierto
        self.pagador_cb.setCurrentIndex(0) # Paciente
        self.toggle_seguro_field("Paciente")
        
        # Emisor reset triggers 'on_emisor_changed' which loads hotels.
        # We need to ensure hotel is CLEARED after that trigger.
        self.emisor_cb.blockSignals(True)
        self.emisor_cb.setCurrentIndex(0)
        self.emisor_cb.blockSignals(False)
        
        # Manually reload hotels if needed to match Emisor 0, 
        # but strictly CLEAR the selection afterwards
        self._reload_hotels() 
        self.hotel_cb.setCurrentIndex(-1)
        self.hotel_cb.setEditText("")
        if hasattr(self.hotel_cb, "lineEdit") and self.hotel_cb.lineEdit():
             self.hotel_cb.lineEdit().clear()

    def save(self):
        if not self.paciente_edit.text().strip():
            QMessageBox.warning(self, "Campo Obligatorio", "El campo 'Paciente' es obligatorio.\nPor favor, introduzca el nombre del paciente.")
            return
        
        # Validar que NHC sea obligatorio si Requiere Traslado está marcado
        if self.traslado_chk.isChecked() and not self.historia_edit.text().strip():
            QMessageBox.warning(self, "Campo Obligatorio", "El campo 'NHC' es obligatorio cuando se requiere traslado.\nPor favor, introduzca el número de historia clínica.")
            return
        
        # Validar que NHC sea numérico si tiene valor
        nhc_value = self.historia_edit.text().strip()
        if nhc_value and not nhc_value.isdigit():
            QMessageBox.warning(self, "Formato Incorrecto", "El NHC tiene que ser un número.")
            return

        data = {
            "Emisor": self.emisor_cb.currentText(),
            "Hora Solicitud": self.hora_solicitud_edit.time().toString("HH:mm"),
            "Fecha": self.fecha_edit.date().toString("yyyy-MM-dd"),
            "Hotel": self.hotel_cb.currentText(),
            "Habitacion": self.habitacion_edit.text(),
            "Estado": self.estado_cb.currentText(),
            "Paciente": self.paciente_edit.text(),
            "Edad": self.edad_spin.value(),
            "Historia Medica": self.historia_edit.text(),
            "Nacionalidad": self.nacionalidad_cb.currentText(),
            "Motivo Urgencia": self.motivo_edit.text(),
            "Pagador": self.pagador_cb.currentText(),
            "Seguro": self.seguro_edit.currentText(),
            "Touroperador": self.touroperador_edit.currentText(),
            "Hora Avisos": self.hora_avisos_edit.time().toString("HH:mm"),
            "Hora Finalizacion": self.hora_fin_edit.time().toString("HH:mm"),
            "Medico": self.medico_edit.currentText(),
            "Diagnostico": self.diagnostico_edit.text(),
            "Traslado": "Si" if self.traslado_chk.isChecked() else "No",
            "Tipo Traslado": self.tipo_traslado_cb.currentText() if self.traslado_chk.isChecked() else "",
            "Hora Ambulancia": self.hora_ambulancia_edit.time().toString("HH:mm") if (self.traslado_chk.isChecked() and self.hora_ambulancia_edit.isEnabled()) else "",
            "Ingreso": self.ingreso_cb.currentText(),
            "Medico Ingreso": self.medico_ingreso_cb.currentText(),
            "Observaciones": self.observaciones_edit.toPlainText()
        }

        if self.edit_mode_index >= 0:
            success, msg = AvisoManager.update_aviso(self.edit_mode_index, data)
        else:
            success, msg = AvisoManager.create_aviso(data)

        if success:
            QMessageBox.information(self, "Sistema", msg)
            self.reset_form()
            self.saved_signal.emit(data["Estado"])
        else:
            QMessageBox.critical(self, "Error", f"Fallo en la operación:\n{msg}")

    def refresh_doctors(self):
        current_med = self.medico_edit.currentText()
        current_ing = self.medico_ingreso_cb.currentText()
        
        medicos = [m["Nombre"] for m in MedicoManager.load_medicos()]
        
        self.medico_edit.clear()
        self.medico_edit.addItems(medicos)
        self.medico_edit.setCurrentText(current_med)
        
        self.medico_ingreso_cb.clear()
        self.medico_ingreso_cb.addItems(medicos)
        self.medico_ingreso_cb.setCurrentText(current_ing)

class AvisosList(QWidget):
    request_edit = pyqtSignal(int, dict)

    def __init__(self, filter_status=None):
        super().__init__()
        self.filter_status = filter_status
        
        layout = QVBoxLayout(self)

        # --- Date Filter Controls ---
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Filtrar por Fecha:"))
        
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setStyleSheet("font-size: 14px; padding: 5px; min-width: 120px;")
        self.date_edit.dateChanged.connect(self.load_data)
        filter_layout.addWidget(self.date_edit)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        # ----------------------------
        
        self.info_lbl = QLabel("Doble click para editar | Click derecho para eliminar")
        self.info_lbl.setStyleSheet("color: #777; font-size: 12px; font-style: italic;")
        layout.addWidget(self.info_lbl)

        self.table = QTableWidget()
        # Use ALL fields from Manager
        columns = AvisoManager.FIELDS
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        
        # Optimize column widths
        header = self.table.horizontalHeader()
        # Enable scrolling by setting a minimum section size and default to Interactive/ResizeToContents
        header.setDefaultSectionSize(120)
        header.setStretchLastSection(False) 
        # Make specific important columns resize to contents for better visibility
        # FIELDS: ["Emisor", "Hora Solicitud", "Fecha", "Hotel", "Estado", "Paciente", ...]
        # Map indices if needed, or just set all to Interactive so user can resize
        for i in range(len(columns)):
             header.setSectionResizeMode(i, QHeaderView.ResizeMode.Interactive)
        
        # Ensure scroll
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.open_menu)
        self.table.cellDoubleClicked.connect(self.on_double_click)
        
        layout.addWidget(self.table)
        
        # Buttons Layout (Bottom Right)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        # Style helper
        btn_style = """
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px;
                min-width: 180px;
            }
        """

         # Color logic helper
        self.status_colors = {
            "Abierto": QColor("#ff3333"),
            "Anulado": QColor("#888888"),
            "Cerrado": QColor("#00ff00")
        }

        if self.filter_status == "Abierto":
            self.refresh_btn = QPushButton("🔄 REFRESCAR LISTA")
            self.refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.refresh_btn.setStyleSheet(btn_style + """
                QPushButton {
                    background-color: #101014;
                    border: 2px solid #00f3ff;
                    color: #00f3ff;
                }
                QPushButton:hover {
                    background-color: #00f3ff;
                    color: black;
                }
            """)
            self.refresh_btn.clicked.connect(self.load_data)
            btn_layout.addWidget(self.refresh_btn)

        self.export_btn = QPushButton("📊 EXPORTAR A EXCEL")
        self.export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.export_btn.setStyleSheet(btn_style + """
            QPushButton {
                background-color: #101014;
                border: 2px solid #00ff00;
                color: #00ff00;
            }
            QPushButton:hover {
                background-color: #00ff00;
                color: black;
            }
        """)
        self.export_btn.clicked.connect(self.export_data)
        btn_layout.addWidget(self.export_btn)

        self.delete_btn = QPushButton("🗑️ BORRAR AVISO")
        self.delete_btn.setObjectName("DeleteBtn")
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.setStyleSheet(btn_style) # The object name will trigger the specific style
        
        # Only show delete button if NOT in "TODOS" tab (filter_status != None)
        if self.filter_status is not None:
            btn_layout.addWidget(self.delete_btn)
        
        # Summary button to view selected aviso
        self.summary_btn = QPushButton("👁️ VER RESUMEN")
        self.summary_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.summary_btn.setStyleSheet(btn_style + """
            QPushButton { background-color: #222; border: 2px solid #00f3ff; color: #00f3ff; }
            QPushButton:hover { background-color: #00f3ff; color: black; }
        """)
        btn_layout.addWidget(self.summary_btn)

        # Set initial state for action buttons
        self.summary_btn.setEnabled(False)
        if self.filter_status is not None:
            self.delete_btn.setEnabled(False)
        
        layout.addLayout(btn_layout)

        # Connect button signals
        self.summary_btn.clicked.connect(self.on_summary_button)
        self.delete_btn.clicked.connect(self.on_delete_button_clicked)

        # Enable summary/delete buttons when selection changes
        sel_model = self.table.selectionModel()
        sel_model.selectionChanged.connect(self._update_summary_button_state)

        self.current_data_map = {}

    def export_data(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Guardar Archivo", "Export_Avisos.ods", "ODS Files (*.ods);;Excel Files (*.xlsx)")
        if file_name:
            success, msg = AvisoManager.export_to_excel(file_name)
            if success:
                QMessageBox.information(self, "Exportar", msg)
            else:
                QMessageBox.critical(self, "Error", f"Fallo al exportar:\n{msg}")

    def load_data(self):
        self.table.setRowCount(0)
        self.current_data_map = {}
        all_avisos = AvisoManager.load_avisos()
        
        target_date = self.date_edit.date().toString("yyyy-MM-dd")
        # filter_by_date is now IMPLIED as ALWAYS TRUE

        filtered_avisos = []
        for aviso in all_avisos:
            # 1. Status Filter
            estado = aviso.get("Estado", "")
            if self.filter_status == "Abierto" and estado != "Abierto":
                continue
            if self.filter_status == "Cerrado" and estado == "Abierto":
                continue
            
            # 2. Date Filter
            aviso_date = aviso.get("Fecha", "")
            if aviso_date != target_date:
                continue

            filtered_avisos.append(aviso)
        
        self.table.setRowCount(len(filtered_avisos))
        columns = AvisoManager.FIELDS
        
        for i, row_data in enumerate(filtered_avisos):
            self.current_data_map[i] = row_data['_id']
            
            for col_idx, field in enumerate(columns):
                value = str(row_data.get(field, ""))
                item = QTableWidgetItem(value)
                
                # Apply color to Status column (which is 'Estado')
                if field == "Estado":
                   item.setForeground(self.status_colors.get(value, QColor("white")))
                
                self.table.setItem(i, col_idx, item)

    def open_menu(self, position):
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu { background-color: #1a1a25; border: 1px solid #00f3ff; color: white; }
            QMenu::item:selected { background-color: #00f3ff; color: black; }
        """)
        summary_action = menu.addAction("Ver Resumen")
        edit_action = menu.addAction("Editar Aviso")
        del_action = menu.addAction("Eliminar Aviso")
        
        action = menu.exec(self.table.viewport().mapToGlobal(position))
        
        row = self.table.currentRow()
        if row < 0: return

        if action == summary_action:
            original_idx = self.current_data_map.get(row)
            if original_idx is None:
                return
            all_data = AvisoManager.load_avisos()
            if not (0 <= original_idx < len(all_data)):
                return
            data = all_data[original_idx]
            dialog = AvisoSummaryDialog(data, original_idx, parent=self)
            dialog.exec()
            if dialog.changed:
                self.load_data()
        elif action == edit_action:
            self.on_double_click(row, 0)
        elif action == del_action:
            self.delete_row(row)

    def on_double_click(self, row, col):
        original_idx = self.current_data_map.get(row)
        if original_idx is None: return

        all_data = AvisoManager.load_avisos()
        if 0 <= original_idx < len(all_data):
            data = all_data[original_idx]
            
            # The form itself will now handle the editability of closed notices.
            # We always open the editor.
            self.request_edit.emit(original_idx, data)

    def on_delete_button_clicked(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Fila no seleccionada", "Por favor, seleccione un aviso de la lista para eliminar.")
            return
        self.delete_row(row)

    

    def delete_row(self, row):
        original_idx = self.current_data_map.get(row)
        if original_idx is None: return

        # First, get the item's data to check its status
        all_data = AvisoManager.load_avisos()
        if not (0 <= original_idx < len(all_data)):
            return 
        
        data = all_data[original_idx]
        
        # Prevent deletion if the notice is closed
        if data.get("Estado") == "Cerrado":
            QMessageBox.warning(self, "Acción no permitida", "No se puede borrar un aviso cerrado.")
            return
        
        confirm = QMessageBox.question(self, "Confirmar", "¿Estás seguro de eliminar este registro?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            success, msg = AvisoManager.delete_aviso(original_idx)
            if success:
                self.load_data()
            else:
                QMessageBox.warning(self, "Error", msg)

    def _update_summary_button_state(self):
        row = self.table.currentRow()
        is_row_selected = (row >= 0)
        self.summary_btn.setEnabled(is_row_selected)
        self.delete_btn.setEnabled(is_row_selected)

    def on_summary_button(self):
        row = self.table.currentRow()
        if row < 0:
            return
        original_idx = self.current_data_map.get(row)
        if original_idx is None:
            return
        all_data = AvisoManager.load_avisos()
        if not (0 <= original_idx < len(all_data)):
            return
        data = all_data[original_idx]
        dialog = AvisoSummaryDialog(data, original_idx, parent=self)
        dialog.exec()
        if dialog.changed:
            self.load_data()


class AvisoSummaryDialog(QDialog):
    """Dialog showing a detailed summary of an aviso with option to 'Cerrar Aviso'."""
    def __init__(self, data: dict, index: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Resumen del Aviso")
        self.setModal(True)
        # Resize dialog to use most of available screen so content fits without scrolling
        try:
            screen = QApplication.primaryScreen().availableGeometry()
            w = int(screen.width() * 0.9)
            h = int(screen.height() * 0.85)
            self.resize(w, h)
        except Exception:
            self.resize(900, 600)
        self.changed = False
        self.data = dict(data)
        self.index = index

        layout = QVBoxLayout(self)

        title = QLabel(f"Resumen - {self.data.get('Paciente','(Sin nombre)')}")
        title.setStyleSheet('font-size:16px; font-weight:bold;')
        layout.addWidget(title)

        # Build schematic HTML summary for quick understanding
        schematic_html = create_schematic_html(self.data)
        
        # Add observations section if present
        observaciones = self.data.get('Observaciones', '').strip()
        if observaciones:
            observ_html = f"<div style='background:#1a1a1a;color:#ffdca3;padding:12px;border-radius:6px;margin-top:16px'><b>Observaciones:</b><br/>{observaciones.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace(chr(10), '<br/>')}</div>"
        else:
            observ_html = ""
        
        # Add hotel and room info
        hotel = self.data.get('Hotel', '-')
        habitacion = self.data.get('Habitacion', '-')
        hotel_html = f"<div style='margin-top:12px;padding:8px;background:#0d0d0d;border-radius:6px'><b>Hotel:</b> {hotel} &nbsp;&nbsp; <b>Habitación:</b> {habitacion}</div>"
        
        full_html = schematic_html + '\n' + hotel_html + '\n' + observ_html

        summary = QTextEdit()
        summary.setReadOnly(True)
        summary.setHtml(full_html)

        # Set a reasonable fixed height to avoid scrolling
        summary.setMinimumHeight(400)
        summary.setMaximumHeight(500)

        layout.addWidget(summary)

        btns = QHBoxLayout()
        btns.addStretch()

        self.edit_btn = QPushButton("Editar")
        self.edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.edit_btn.clicked.connect(self.on_edit_aviso)
        btns.addWidget(self.edit_btn)

        self.close_btn = QPushButton("Cerrar")
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.clicked.connect(self.accept)
        btns.addWidget(self.close_btn)

        layout.addLayout(btns)

    def on_close_aviso(self):
        # Mark as closed and persist
        self.data["Estado"] = "Cerrado"
        success, msg = AvisoManager.update_aviso(self.index, self.data)
        if success:
            QMessageBox.information(self, "Aviso cerrado", "El aviso se ha marcado como CERRADO.")
            self.changed = True
            self.accept()
        else:
            QMessageBox.warning(self, "Error", f"No se pudo cerrar el aviso:\n{msg}")

    def on_edit_aviso(self):
        # Try to ask parent/list to open the editor
        parent = self.parent()
        try:
            if hasattr(parent, 'request_edit'):
                parent.request_edit.emit(self.index, self.data)
                self.accept()
                return
        except Exception:
            pass

        # Fallback: try to call go_to_edit on top-level window
        try:
            top = self.window()
            if hasattr(top, 'go_to_edit'):
                top.go_to_edit(self.index, self.data)
                self.accept()
                return
        except Exception:
            pass

        QMessageBox.warning(self, "Editar no disponible", "No se pudo iniciar la edición desde aquí.")


class DashboardTab(QWidget):
    """Dashboard with advanced search and filtering capabilities"""
    
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("📊 DASHBOARD - BÚSQUEDA AVANZADA")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Top Panel: Search Filters on LEFT, Charts on RIGHT
        top_panel = QWidget()
        top_layout = QHBoxLayout(top_panel)
        top_layout.setSpacing(15)
        
        # RIGHT SIDE: Statistics Panel with Charts
        stats_panel = QWidget()
        stats_panel.setStyleSheet("""
            QWidget {
                background-color: #0d0d0d;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        stats_layout = QVBoxLayout(stats_panel)
        
        # Create two charts (compact vertical layout)
        self.fig = Figure(figsize=(4, 4), facecolor='#0d0d0d')
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setStyleSheet("background-color: #0d0d0d;")
        self.canvas.setMaximumWidth(400)  # Limit width
        
        # Chart 1: Estados (Pie Chart) - TOP
        self.ax1 = self.fig.add_subplot(211)
        self.ax1.set_facecolor('#0d0d0d')
        
        # Chart 2: Top 5 Hoteles (Bar Chart) - BOTTOM
        self.ax2 = self.fig.add_subplot(212)
        self.ax2.set_facecolor('#0d0d0d')
        
        stats_layout.addWidget(self.canvas)
        
        # LEFT SIDE: Search Panel
        search_panel = QWidget()
        search_panel.setStyleSheet("""
            QWidget {
                background-color: #0d0d0d;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        search_layout = QGridLayout(search_panel)
        search_layout.setSpacing(10)
        
        # Row 0: Date Range
        search_layout.addWidget(QLabel("FECHA DESDE:"), 0, 0, alignment=Qt.AlignmentFlag.AlignRight)
        self.date_from = QDateEdit(QDate.currentDate().addDays(-30))
        self.date_from.setCalendarPopup(True)
        self.date_from.setDisplayFormat("yyyy-MM-dd")
        search_layout.addWidget(self.date_from, 0, 1)
        
        search_layout.addWidget(QLabel("FECHA HASTA:"), 0, 2, alignment=Qt.AlignmentFlag.AlignRight)
        self.date_to = QDateEdit(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        self.date_to.setDisplayFormat("yyyy-MM-dd")
        search_layout.addWidget(self.date_to, 0, 3)
        
        # Row 1: Emisor and Hotel
        search_layout.addWidget(QLabel("EMISOR:"), 1, 0, alignment=Qt.AlignmentFlag.AlignRight)
        self.emisor_filter = QComboBox()
        self.emisor_filter.addItem("(Todos)")
        self.emisor_filter.addItems(["Jaime", "Guia", "Paciente", "Seguro", "SMCS", "VITHAS", "RECEPCION", "GP"])
        search_layout.addWidget(self.emisor_filter, 1, 1)
        
        search_layout.addWidget(QLabel("HOTEL:"), 1, 2, alignment=Qt.AlignmentFlag.AlignRight)
        self.hotel_filter = QComboBox()
        self.hotel_filter.setEditable(True)
        self.hotel_filter.addItem("(Todos)")
        self._load_hotels()
        search_layout.addWidget(self.hotel_filter, 1, 3)
        
        # Row 2: Seguro and Touroperador
        search_layout.addWidget(QLabel("SEGURO:"), 2, 0, alignment=Qt.AlignmentFlag.AlignRight)
        self.seguro_filter = QComboBox()
        self.seguro_filter.setEditable(True)
        self.seguro_filter.addItem("(Todos)")
        self._load_seguros()
        search_layout.addWidget(self.seguro_filter, 2, 1)
        
        search_layout.addWidget(QLabel("TOUROPERADOR:"), 2, 2, alignment=Qt.AlignmentFlag.AlignRight)
        self.ttoo_filter = QComboBox()
        self.ttoo_filter.setEditable(True)
        self.ttoo_filter.addItem("(Todos)")
        self._load_ttoos()
        search_layout.addWidget(self.ttoo_filter, 2, 3)
        
        # Row 3: Ingreso and Estado
        search_layout.addWidget(QLabel("INGRESO:"), 3, 0, alignment=Qt.AlignmentFlag.AlignRight)
        self.ingreso_filter = QComboBox()
        self.ingreso_filter.addItems(["(Todos)", "No ingresa", "Planta", "UCI"])
        search_layout.addWidget(self.ingreso_filter, 3, 1)
        
        search_layout.addWidget(QLabel("ESTADO:"), 3, 2, alignment=Qt.AlignmentFlag.AlignRight)
        self.estado_filter = QComboBox()
        self.estado_filter.addItems(["(Todos)", "Abierto", "Cerrado", "Anulado"])
        self.estado_filter.setCurrentText("Cerrado")  # Default to Cerrado
        search_layout.addWidget(self.estado_filter, 3, 3)
        
        # Row 4: Search Button
        self.search_btn = QPushButton("🔍 BUSCAR")
        self.search_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.search_btn.clicked.connect(self.perform_search)
        self.search_btn.setStyleSheet("""
            QPushButton {
                background-color: #00f3ff;
                color: black;
                padding: 10px 30px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #00d4dd;
            }
        """)
        search_layout.addWidget(self.search_btn, 4, 0, 1, 2)
        
        self.clear_btn = QPushButton("🗑️ LIMPIAR FILTROS")
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_btn.clicked.connect(self.clear_filters)
        search_layout.addWidget(self.clear_btn, 4, 2, 1, 2)
        
        # Add search panel to LEFT side of top layout
        top_layout.addWidget(search_panel)
        
        # Add charts panel to RIGHT side of top layout
        top_layout.addWidget(stats_panel)
        
        # Add the complete top panel (charts + search) to main layout
        layout.addWidget(top_panel)
        
        # Results Label
        self.results_label = QLabel("Resultados: 0 avisos encontrados")
        self.results_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px;")
        layout.addWidget(self.results_label)
        
        # Results Table
        self.table = QTableWidget()
        self.table.setColumnCount(len(AvisoManager.FIELDS))
        self.table.setHorizontalHeaderLabels(AvisoManager.FIELDS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table)
        
        # Export Button
        export_layout = QHBoxLayout()
        export_layout.addStretch()
        
        self.export_btn = QPushButton("📊 EXPORTAR RESULTADOS A EXCEL")
        self.export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.export_btn.clicked.connect(self.export_results)
        export_layout.addWidget(self.export_btn)
        
        layout.addLayout(export_layout)
        
        # Store current results
        self.current_results = []
        
        # Perform initial search
        self.perform_search()
    
    def update_charts(self, avisos):
        """Update both charts with current data"""
        # Clear all axes
        self.ax1.clear()
        self.ax2.clear()
        
        # Set dark theme colors
        text_color = '#00f3ff'
        grid_color = '#333333'
        
        # Chart 1: Top 5 Hoteles Distribution (Pie Chart)
        hoteles_count = {}
        for aviso in avisos:
            hotel = aviso.get("Hotel", "Desconocido")
            if hotel and hotel.strip():
                hoteles_count[hotel] = hoteles_count.get(hotel, 0) + 1
        
        if hoteles_count:
            # Get top 5 hoteles for pie chart
            top_hoteles_pie = sorted(hoteles_count.items(), key=lambda x: x[1], reverse=True)[:5]
            hotels_pie = [h[0][:25] + '...' if len(h[0]) > 25 else h[0] for h in top_hoteles_pie]
            counts_pie = [h[1] for h in top_hoteles_pie]
            
            # Generate vibrant colors for each hotel
            colors = ['#00cc66', '#ff4444', '#ffcc00', '#00f3ff', '#bc13fe']
            explode = [0.05] * len(hotels_pie)  # Slight separation
            
            wedges, texts, autotexts = self.ax1.pie(
                counts_pie,
                labels=hotels_pie,
                autopct='%1.1f%%',
                colors=colors[:len(hotels_pie)],
                explode=explode,
                shadow=True,
                startangle=90,
                textprops={'color': text_color, 'fontsize': 8, 'weight': 'bold'}
            )
            
            for autotext in autotexts:
                autotext.set_color('black')
                autotext.set_weight('bold')
                autotext.set_fontsize(7)
            
            self.ax1.set_title('Top 5 Hoteles', color=text_color, fontsize=10, weight='bold', pad=10)
        else:
            self.ax1.text(0.5, 0.5, 'Sin datos', ha='center', va='center', 
                         color=text_color, fontsize=14, transform=self.ax1.transAxes)
            self.ax1.set_title('Top 5 Hoteles', color=text_color, fontsize=12, weight='bold')
        
        # Chart 2: Top 5 Hoteles (Bar Chart)
        if hoteles_count:
            # Get top 5
            top_hoteles = sorted(hoteles_count.items(), key=lambda x: x[1], reverse=True)[:5]
            hotels = [h[0][:20] + '...' if len(h[0]) > 20 else h[0] for h in top_hoteles]  # Truncate long names
            counts = [h[1] for h in top_hoteles]
            
            bars = self.ax2.barh(hotels, counts, color='#00f3ff', edgecolor='#00d4dd', linewidth=2)
            
            # Add value labels on bars
            for i, (bar, count) in enumerate(zip(bars, counts)):
                self.ax2.text(count, i, f' {count}', va='center', color=text_color, 
                            fontsize=7, weight='bold')
            
            self.ax2.set_xlabel('Avisos', color=text_color, fontsize=8, weight='bold')
            self.ax2.set_title('Top 5 Hoteles (Barras)', color=text_color, fontsize=10, weight='bold', pad=10)
            self.ax2.tick_params(colors=text_color, labelsize=7)
            self.ax2.spines['bottom'].set_color(grid_color)
            self.ax2.spines['left'].set_color(grid_color)
            self.ax2.spines['top'].set_visible(False)
            self.ax2.spines['right'].set_visible(False)
            self.ax2.grid(axis='x', alpha=0.3, color=grid_color)
        else:
            self.ax2.text(0.5, 0.5, 'Sin datos', ha='center', va='center', 
                         color=text_color, fontsize=14, transform=self.ax2.transAxes)
            self.ax2.set_title('Top 5 Hoteles (Barras)', color=text_color, fontsize=12, weight='bold')
        
        # Adjust layout and refresh
        self.fig.tight_layout()
        self.canvas.draw()
    
    def _load_hotels(self):
        """Load unique hotels from database"""
        try:
            hotels = HotelManager.load_hotels()
            hotel_names = sorted(set([h.get("Nombre", "") for h in hotels if h.get("Nombre")]))
            self.hotel_filter.addItems(hotel_names)
        except Exception:
            pass
    
    def _load_seguros(self):
        """Load unique seguros from avisos"""
        try:
            avisos = AvisoManager.load_avisos()
            seguros = sorted(set([a.get("Seguro", "") for a in avisos if a.get("Seguro") and a.get("Seguro").strip()]))
            self.seguro_filter.addItems(seguros)
        except Exception:
            pass
    
    def _load_ttoos(self):
        """Load unique touroperadores from avisos"""
        try:
            avisos = AvisoManager.load_avisos()
            ttoos = sorted(set([a.get("Touroperador", "") for a in avisos if a.get("Touroperador") and a.get("Touroperador").strip()]))
            self.ttoo_filter.addItems(ttoos)
        except Exception:
            pass
    
    def clear_filters(self):
        """Reset all filters to default"""
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_to.setDate(QDate.currentDate())
        self.emisor_filter.setCurrentIndex(0)
        self.hotel_filter.setCurrentIndex(0)
        self.seguro_filter.setCurrentIndex(0)
        self.ttoo_filter.setCurrentIndex(0)
        self.ingreso_filter.setCurrentIndex(0)
        self.estado_filter.setCurrentIndex(0)
        self.perform_search()
    
    def perform_search(self):
        """Execute search with current filters"""
        all_avisos = AvisoManager.load_avisos()
        
        # Get filter values
        date_from_str = self.date_from.date().toString("yyyy-MM-dd")
        date_to_str = self.date_to.date().toString("yyyy-MM-dd")
        emisor_filter = self.emisor_filter.currentText()
        hotel_filter = self.hotel_filter.currentText()
        seguro_filter = self.seguro_filter.currentText()
        ttoo_filter = self.ttoo_filter.currentText()
        ingreso_filter = self.ingreso_filter.currentText()
        estado_filter = self.estado_filter.currentText()
        
        # Filter avisos
        filtered = []
        for aviso in all_avisos:
            # Date filter
            aviso_date = aviso.get("Fecha", "")
            if aviso_date < date_from_str or aviso_date > date_to_str:
                continue
            
            # Emisor filter
            if emisor_filter != "(Todos)" and aviso.get("Emisor", "") != emisor_filter:
                continue
            
            # Hotel filter
            if hotel_filter != "(Todos)" and aviso.get("Hotel", "") != hotel_filter:
                continue
            
            # Seguro filter
            if seguro_filter != "(Todos)" and aviso.get("Seguro", "") != seguro_filter:
                continue
            
            # Touroperador filter
            if ttoo_filter != "(Todos)" and aviso.get("Touroperador", "") != ttoo_filter:
                continue
            
            # Ingreso filter
            if ingreso_filter != "(Todos)" and aviso.get("Ingreso", "") != ingreso_filter:
                continue
            
            # Estado filter
            if estado_filter != "(Todos)" and aviso.get("Estado", "") != estado_filter:
                continue
            
            filtered.append(aviso)
        
        # Update results
        self.current_results = filtered
        self.results_label.setText(f"Resultados: {len(filtered)} avisos encontrados")
        
        # Update charts with filtered data
        self.update_charts(filtered)
        
        # Populate table
        self.table.setRowCount(len(filtered))
        for i, aviso in enumerate(filtered):
            for col_idx, field in enumerate(AvisoManager.FIELDS):
                value = str(aviso.get(field, ""))
                item = QTableWidgetItem(value)
                
                # Color by estado
                if field == "Estado":
                    estado = aviso.get("Estado", "")
                    if estado == "Cerrado":
                        item.setForeground(QColor("#00cc66"))
                    elif estado == "Abierto":
                        item.setForeground(QColor("#ff4444"))
                
                self.table.setItem(i, col_idx, item)
    
    def export_results(self):
        """Export current search results to Excel"""
        if not self.current_results:
            QMessageBox.warning(self, "Sin Resultados", "No hay resultados para exportar.")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, 
            "Exportar Resultados",
            f"busqueda_avisos_{QDate.currentDate().toString('yyyy-MM-dd')}.xlsx",
            "Excel Files (*.xlsx);;ODS Files (*.ods)"
        )
        
        if filename:
            # Create temporary filtered data
            export_data = []
            for a in self.current_results:
                def val(key):
                    v = a.get(key, "")
                    if v is None: return "N/A"
                    s = str(v).strip()
                    return s if s else "N/A"
                
                hotel_name = val("Hotel")
                municipio, zona = HotelLocationManager.get_location(hotel_name)
                
                row = {
                    "FECHA": val("Fecha"),
                    "TIPO EMISOR": val("Emisor"),
                    "EMISOR": hotel_name,
                    "HAB.": val("Habitacion"),
                    "TTOO": val("Touroperador"),
                    "MOTIVO LLAMADA": val("Motivo Urgencia"),
                    "NOMBRE PACIENTE": val("Paciente"),
                    "NHC A XANIT": val("Historia Medica"),
                    "MEDICO DE URGENCIAS": val("Medico"),
                    "OBSERVACIONES": val("Observaciones"),
                    "MUNICIPIO": municipio,
                    "ZONA AVISO": zona
                }
                export_data.append(row)
            
            try:
                df = pd.DataFrame(export_data)
                cols = ["FECHA", "TIPO EMISOR", "EMISOR", "HAB.", "TTOO", "MOTIVO LLAMADA",
                        "NOMBRE PACIENTE", "NHC A XANIT", "MEDICO DE URGENCIAS", "OBSERVACIONES",
                        "MUNICIPIO", "ZONA AVISO"]
                
                for col in cols:
                    if col not in df.columns:
                        df[col] = ""
                
                df = df[cols]
                
                if filename.endswith(".ods"):
                    df.to_excel(filename, engine="odf", index=False)
                else:
                    df.to_excel(filename, index=False)
                
                QMessageBox.information(self, "Éxito", f"Resultados exportados correctamente a:\n{filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al exportar:\n{str(e)}")


class MapaAvisosTab(QWidget):
    """Interactive map showing active avisos in real-time"""
    
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Title and controls
        header_layout = QHBoxLayout()
        
        title = QLabel("🗺️ MAPA DE AVISOS ACTIVOS")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Filter controls
        filter_label = QLabel("Mostrar:")
        header_layout.addWidget(filter_label)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Todos los Avisos", "Solo Abiertos", "Abiertos + Cerrados Hoy"])
        self.filter_combo.setCurrentIndex(0)  # Default to "Todos los Avisos"
        self.filter_combo.currentTextChanged.connect(self.update_map)
        header_layout.addWidget(self.filter_combo)
        
        # Refresh button
        self.refresh_btn = QPushButton("🔄 ACTUALIZAR")
        self.refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_btn.clicked.connect(self.update_map)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #00f3ff;
                color: black;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00d4dd;
            }
        """)
        header_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Info label
        self.info_label = QLabel("Cargando mapa...")
        self.info_label.setStyleSheet("color: #00f3ff; font-size: 12px; margin: 5px;")
        layout.addWidget(self.info_label)
        
        # Map view
        if WEBENGINE_AVAILABLE:
            self.map_view = QWebEngineView()
            layout.addWidget(self.map_view)
        else:
            error_label = QLabel("⚠️ QWebEngineView no disponible.\nInstala PyQt6-WebEngine para ver el mapa.")
            error_label.setStyleSheet("color: #ff4444; font-size: 14px; padding: 20px;")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(error_label)
            return
        
        # Legend
        legend_layout = QHBoxLayout()
        legend_layout.addStretch()
        
        legend_items = [
            ("🔴", "Abierto", "#ff4444"),
            ("🟢", "Cerrado", "#00cc66"),
            ("⚪", "Anulado", "#888888"),
            ("🏥", "Vithas Xanit", "#0055a4")
        ]
        
        for icon, text, color in legend_items:
            item_layout = QHBoxLayout()
            icon_label = QLabel(icon)
            icon_label.setStyleSheet(f"font-size: 16px;")
            text_label = QLabel(text)
            text_label.setStyleSheet(f"color: {color}; font-weight: bold; margin-right: 15px;")
            item_layout.addWidget(icon_label)
            item_layout.addWidget(text_label)
            legend_layout.addLayout(item_layout)
        
        legend_layout.addStretch()
        layout.addLayout(legend_layout)
        
        # Generate initial map
        self.update_map()
    
    def update_map(self):
        """Generate and display the map with current avisos"""
        if not WEBENGINE_AVAILABLE:
            return
        
        # Load avisos
        all_avisos = AvisoManager.load_avisos()
        
        # Filter based on selection
        filter_mode = self.filter_combo.currentText()
        today = QDate.currentDate().toString("yyyy-MM-dd")
        
        if filter_mode == "Solo Abiertos":
            avisos = [a for a in all_avisos if a.get("Estado") == "Abierto"]
        elif filter_mode == "Abiertos + Cerrados Hoy":
            avisos = [a for a in all_avisos if a.get("Estado") == "Abierto" or 
                     (a.get("Estado") == "Cerrado" and a.get("Fecha") == today)]
        else:  # Todos los Avisos
            avisos = all_avisos
        
        # Create map centered on Costa del Sol
        mapa = folium.Map(
            location=[36.5, -4.8],  # Costa del Sol center
            zoom_start=10,
            tiles='OpenStreetMap'
        )
        
        # Add Vithas Xanit marker
        folium.Marker(
            location=[36.5074, -4.8827],  # Vithas Xanit Benalmádena
            popup="<b>🏥 Vithas Xanit International</b><br>Hospital Base",
            tooltip="Vithas Xanit",
            icon=folium.Icon(color='blue', icon='hospital-o', prefix='fa')
        ).add_to(mapa)
        
        # Group markers for clustering
        marker_cluster = plugins.MarkerCluster().add_to(mapa)
        
        # Add markers for each aviso
        avisos_con_ubicacion = 0
        coords_cache = load_coords_cache()
        
        # Predefined coordinates for common hotels to avoid slow API calls
        HOTEL_COORDS = {
            "Gran Hotel Miramar GL (Malaga)": (36.7213, -4.4214),
            "BYPILLOW California": (36.5074, -4.8827),
            "Hotel Claude (Marbella)": (36.5095, -4.8826),
            "Casa Diez (Estepona)": (36.4279, -5.1448),
            "Amanhavis Hotel (Benahavis)": (36.5074, -5.0500),
            "El Fuerte Marbella": (36.5095, -4.8826),
            "Melia Costa Del Sol": (36.6189, -4.4991),
            "Catalonia Málaga": (36.7213, -4.4214),
            "Eurostars Oasis Marbella": (36.5095, -4.8826),
            "Casa la Concha (Marbella)": (36.5095, -4.8826),
            "VITHAS BENALMADENA": (36.5974, -4.5167),
            "Iberostar Malaga Playa": (36.6189, -4.4991),
            "Hotel Guadalmina Spa & Golf Resort": (36.4800, -5.0300),
            "Vincci Selección Aleysa": (36.5095, -4.8826),
            "Don Carlos Resort & Spa": (36.5095, -4.8826),
            "Marriott's Playa Andaluza": (36.4800, -5.0300),
            "Kempinski Hotel Bahía": (36.4800, -5.0300),
            "Puente Romano Beach Resort": (36.5095, -4.8826)
        }
        
        for aviso in avisos:
            hotel_name = aviso.get("Hotel", "")
            if not hotel_name:
                continue
            
            # Try predefined coordinates first
            coords = HOTEL_COORDS.get(hotel_name)
            
            # Then try cache
            if not coords:
                coords = coords_cache.get(hotel_name)
            
            # Skip geocoding for now to avoid blocking the UI
            # User can manually geocode later if needed
            
            if not coords:
                continue
            
            avisos_con_ubicacion += 1
            
            # Determine marker color based on estado
            estado = aviso.get("Estado", "")
            if estado == "Abierto":
                color = 'red'
                icon_color = '#ff4444'
            elif estado == "Cerrado":
                color = 'green'
                icon_color = '#00cc66'
            else:  # Anulado
                color = 'gray'
                icon_color = '#888888'
            
            # Create popup content
            paciente = aviso.get("Paciente", "N/A")
            motivo = aviso.get("Motivo Urgencia", "N/A")
            fecha = aviso.get("Fecha", "N/A")
            hora = aviso.get("Hora Solicitud", "N/A")
            medico = aviso.get("Medico", "N/A")
            diagnostico = aviso.get("Diagnostico", "N/A")
            
            popup_html = f"""
            <div style='width: 250px; font-family: Arial;'>
                <h4 style='margin: 0; color: {icon_color};'>{estado}</h4>
                <hr style='margin: 5px 0;'>
                <b>🏨 Hotel:</b> {hotel_name}<br>
                <b>👤 Paciente:</b> {paciente}<br>
                <b>📅 Fecha:</b> {fecha} {hora}<br>
                <b>⚕️ Motivo:</b> {motivo}<br>
                {f'<b>👨‍⚕️ Médico:</b> {medico}<br>' if medico != 'N/A' else ''}
                {f'<b>🩺 Diagnóstico:</b> {diagnostico}<br>' if diagnostico != 'N/A' else ''}
            </div>
            """
            
            # Add marker
            folium.Marker(
                location=coords,
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"{hotel_name} - {estado}",
                icon=folium.Icon(color=color, icon='info-sign')
            ).add_to(marker_cluster)
        
        # Update info label
        print(f"[DEBUG] Total avisos cargados: {len(all_avisos)}")
        print(f"[DEBUG] Avisos después de filtro '{filter_mode}': {len(avisos)}")
        print(f"[DEBUG] Avisos con ubicación en mapa: {avisos_con_ubicacion}")
        
        self.info_label.setText(
            f"📍 Mostrando {avisos_con_ubicacion} avisos de {len(avisos)} totales en el mapa | "
            f"Filtro: {filter_mode}"
        )
        
        # Save map to temp file and load it
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html', encoding='utf-8') as f:
            mapa.save(f.name)
            self.map_view.setUrl(QUrl.fromLocalFile(f.name))


class ModernMedicalApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FUTURISTIC MEDICAL MANAGER v5.0 (NEON EDITION)")
        self.resize(1200, 800)
        self.setMinimumSize(1000, 700)
        
        self.is_neon_mode = True
        self.setStyleSheet(get_neon_stylesheet())
        
        main_layout = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)
        
        # Header Layout for Logo and Theme Toggle
        header_layout = QHBoxLayout()
        
        # Common Header Button Style
        header_btn_style = """
            QPushButton {
                background-color: #1a1a25;
                color: #e0e0e0;
                border: 1px solid #00f3ff;
                padding: 10px 20px;
                border-radius: 20px;
                font-weight: bold;
                min-width: 140px;
            }
            QPushButton:hover {
                background-color: #00f3ff;
                color: black;
            }
        """

        # 1. Left Button: Light/Dark Mode
        self.theme_btn = QPushButton("☀️ Light Mode")
        self.theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_btn.clicked.connect(self.toggle_theme)
        self.theme_btn.setStyleSheet(header_btn_style)
        header_layout.addWidget(self.theme_btn)
        
        header_layout.addStretch()

        # 2. Center: Logo
        self.logo_lbl = ClickableLabel(self)
        if os.path.exists("logo.png"):
            pixmap = QPixmap("logo.png")
            scaled_pixmap = pixmap.scaledToHeight(100, Qt.TransformationMode.SmoothTransformation)
            self.logo_lbl.setPixmap(scaled_pixmap)
        else:
            self.logo_lbl.setText("🏥 MEDICAL MANAGER")
            self.logo_lbl.setStyleSheet("font-size: 24px; color: #00f3ff; font-weight: bold; letter-spacing: 2px;")
        
        self.logo_lbl.setCursor(Qt.CursorShape.PointingHandCursor)
        self.logo_lbl.clicked.connect(self.toggle_logo_animation)
        header_layout.addWidget(self.logo_lbl)
        
        header_layout.addStretch()

        # 3. Right Button: Vithas Mode
        self.vithas_btn = QPushButton("🏥 Modo Vithas")
        self.vithas_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.vithas_btn.clicked.connect(self.toggle_vithas_mode)
        self.vithas_btn.setStyleSheet(header_btn_style)
        header_layout.addWidget(self.vithas_btn)
        
        main_layout.addLayout(header_layout)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self.tab_new = AvisoForm()
        self.tab_open = AvisosList(filter_status="Abierto")
        self.tab_closed = AvisosList(filter_status="Cerrado")
        self.tab_all = AvisosList(filter_status=None)
        self.tab_medicos = MedicosTab()
        self.tab_hoteles = HotelesTab()
        self.tab_dashboard = DashboardTab()
        
        # Connect save signal to auto-switch tab
        self.tab_new.saved_signal.connect(self.on_aviso_saved)

        # IMPORTANT: "NUEVO AVISO" is the FIRST tab now
        self.tabs.addTab(self.tab_new, "➕ NUEVO AVISO")
        self.tabs.addTab(self.tab_open, "⚡ AVISOS ABIERTOS")
        self.tabs.addTab(self.tab_closed, "🔒 AVISOS CERRADOS")
        self.tabs.addTab(self.tab_all, "📋 TODOS LOS AVISOS")
        self.tabs.addTab(self.tab_dashboard, "🔍 BÚSQUEDA AVANZADA")
        self.tabs.addTab(self.tab_medicos, "👨‍⚕️ MÉDICOS")
        self.tabs.addTab(self.tab_hoteles, "🏨 HOTELES")
        
        # Connect edit requests
        self.tab_open.request_edit.connect(self.go_to_edit)
        self.tab_closed.request_edit.connect(self.go_to_edit)
        self.tab_all.request_edit.connect(self.go_to_edit)
        
        # Connect tab change to refresh lists
        self.tabs.currentChanged.connect(self.on_tab_change)
        
        # Data cache to avoid redundant CSV reads
        self._avisos_cache = None
        self._cache_timestamp = 0
        
        # Only load the initial tab (NUEVO AVISO) - lazy load others
        self.tab_new.refresh_doctors()
        self.tab_new.refresh_hotels()

    def toggle_theme(self):
        if self.is_neon_mode:
            self.setStyleSheet(get_light_stylesheet())
            self.theme_btn.setText("🌙 Neon Mode")
            self.is_neon_mode = False
        else:
            self.setStyleSheet(get_neon_stylesheet())
            self.theme_btn.setText("☀️ Light Mode")
            self.is_neon_mode = True

    def toggle_vithas_mode(self):
        # Applies "Vithas" theme which uses a background image
        if not os.path.exists("vithas_bg.jpg") and not os.path.exists("vithas_bg.png"):
            QMessageBox.warning(self, "Falta Imagen", "No se encuentra 'vithas_bg.jpg' ni 'vithas_bg.png'.\nPor favor coloca la imagen del logo o fondo en la carpeta de la aplicación.")
            return

        self.setStyleSheet(get_vithas_stylesheet())
        self.is_neon_mode = False # Reset neon flag
        self.theme_btn.setText("🌙 Dark Mode") # Set toggle to allow going back to dark
        
    def on_tab_change(self, index):
        """Only refresh the active tab to improve performance"""
        # Map tab indices to their widgets
        tab_widget = self.tabs.widget(index)
        
        # Index 0: NUEVO AVISO
        if index == 0:
            self.tab_new.refresh_doctors()
            self.tab_new.refresh_hotels()
            self.tab_new.reset_form()
        
        # Index 1: AVISOS ABIERTOS
        elif index == 1:
            self.tab_open.load_data()
        
        # Index 2: AVISOS CERRADOS
        elif index == 2:
            self.tab_closed.load_data()
        
        # Index 3: TODOS LOS AVISOS
        elif index == 3:
            self.tab_all.load_data()
        
        # Index 4: BÚSQUEDA AVANZADA (Dashboard)
        elif index == 4:
            # Dashboard auto-refreshes on perform_search
            pass
        
        # Index 5: MÉDICOS
        elif index == 5:
            self.tab_medicos.load_data()
        
        # Index 6: HOTELES
        elif index == 6:
            self.tab_hoteles.load_data()

    def refresh_all_lists(self):
        self.tab_open.load_data()
        self.tab_closed.load_data()
        self.tab_all.load_data()
        self.tab_medicos.load_data()
        self.tab_hoteles.load_data()

    def on_aviso_saved(self, status):
        # Determine strict tab index
        # 0: Nuevo
        # 1: Abiertos
        # 2: Cerrados
        # 3: Todos
        if status == "Abierto":
            self.tabs.setCurrentIndex(1)
        elif status == "Cerrado":
            self.tabs.setCurrentIndex(2)
        else:
            # Fallback or other status
            self.tabs.setCurrentIndex(3) # Todos

    def go_to_edit(self, index, data):
        # Switch tab FIRST so that on_tab_change (which refreshes/clears hotels)
        # runs BEFORE we load the specific aviso data.
        self.tabs.setCurrentWidget(self.tab_new)
        self.tab_new.load_aviso_for_editing(index, data)

    def toggle_logo_animation(self):
        if not hasattr(self, "_anim_running"):
            self._anim_running = False

        if self._anim_running:
            # STOP
            self._anim_running = False
            if hasattr(self, "_logo_anim"):
                self._logo_anim.stop()
                self._logo_anim.deleteLater()
            
            if hasattr(self, "_logo_proxy"):
                self._logo_proxy.deleteLater()
                del self._logo_proxy

            self.logo_lbl.show()
        else:
            # START
            self._anim_running = True
            
            # Create Proxy
            proxy = ClickableLabel(self) # Use ClickableLabel instead of QLabel
            if self.logo_lbl.pixmap():
                proxy.setPixmap(self.logo_lbl.pixmap())
                proxy.setScaledContents(self.logo_lbl.hasScaledContents())
            else:
                proxy.setText(self.logo_lbl.text())
                proxy.setStyleSheet(self.logo_lbl.styleSheet())
                proxy.setFont(self.logo_lbl.font())
            
            # Connect click on proxy to STOP functionality
            proxy.setCursor(Qt.CursorShape.PointingHandCursor)
            proxy.clicked.connect(self.toggle_logo_animation)
                
            # Position over original
            start_pos = self.logo_lbl.mapTo(self, QPoint(0,0))
            proxy.setGeometry(start_pos.x(), start_pos.y(), self.logo_lbl.width(), self.logo_lbl.height())
            proxy.show()
            proxy.raise_()
            
            # Hide Original
            sp = self.logo_lbl.sizePolicy()
            sp.setRetainSizeWhenHidden(True)
            self.logo_lbl.setSizePolicy(sp)
            self.logo_lbl.hide()
            
            # Animation
            anim = QPropertyAnimation(proxy, b"pos", self)
            anim.setDuration(8000) # 8 seconds full cycle (Slower)
            anim.setLoopCount(-1) # Infinite
            
            # Calculate targets
            # Left Target: right edge of Theme Btn
            left_limit_x = self.theme_btn.mapTo(self, QPoint(0,0)).x() + self.theme_btn.width() + 10
            
            # Right Target: left edge of Vithas Btn - logo width
            right_limit_x = self.vithas_btn.mapTo(self, QPoint(0,0)).x() - proxy.width() - 10
            
            center_x = start_pos.x()
            y = start_pos.y()
            
            # Keyframes: Center -> Left -> Center -> Right -> Center
            anim.setKeyValueAt(0, QPoint(center_x, y))
            anim.setKeyValueAt(0.25, QPoint(left_limit_x, y))
            anim.setKeyValueAt(0.5, QPoint(center_x, y))
            anim.setKeyValueAt(0.75, QPoint(right_limit_x, y))
            anim.setKeyValueAt(1, QPoint(center_x, y))
            
            anim.setEasingCurve(QEasingCurve.Type.InOutSine)
            anim.start()
            
            self._logo_anim = anim
            self._logo_proxy = proxy



def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = ModernMedicalApp()
    window.showMaximized()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
