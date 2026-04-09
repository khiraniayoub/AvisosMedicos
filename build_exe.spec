# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Collect all data files
added_files = [
    ('logo.png', '.'),
    ('vithas_bg.png', '.'),
    ('avisos.csv', '.'),
    ('hoteles.csv', '.'),
    ('medicos.csv', '.'),
    ('hoteles_coords.json', '.'),
    ('teams_config.json', '.'),
    ('.env', '.'),
    ('src', 'src'),
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.QtWebEngineWidgets',
        'matplotlib',
        'matplotlib.backends.backend_qt5agg',
        'folium',
        'folium.plugins',
        'pandas',
        'requests',
        'psycopg2',
        'src.database',
        'src.whatsapp_sender',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Vithas_Avisos',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No mostrar consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Puedes añadir un icono .ico aquí si tienes uno
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Vithas_Avisos',
)
