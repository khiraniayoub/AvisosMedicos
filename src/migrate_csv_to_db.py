import sys
import os
import csv
from src.database import db

# Add project root to path
sys.path.append(os.getcwd())

def migrate():
    print("Starting migration from avisos.csv to PostgreSQL...")
    
    if not os.path.exists("avisos.csv"):
        print("avisos.csv not found. Nothing to migrate.")
        return

    if not db.connect():
        print("Could not connect to database. Check .env configuration.")
        return

    # Initialize table if needed
    db.initialize_db()
    
    # Check if DB is empty to avoid duplicates (naive check)
    rows = db.execute_query("SELECT COUNT(*) as count FROM avisos")
    count = rows[0]['count'] if rows else 0
    if count > 0:
        print(f"Database already has {count} records. Migration paused to prevent duplicates.")
        print("If you want to force migration, clear the table first.")
        # Optional: Ask user input if interactive?
        # return

    # Load CSV
    try:
        with open("avisos.csv", mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            data = list(reader)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    print(f"Found {len(data)} records in CSV. Inserting...")
    
    # Re-use AvisoManager mapping logic or manual insert?
    # Manual insert is safer to ensure we use the same mapping logic as the app.
    # But since I can't easily import AvisoManager without importing main (which runs GUI stuff),
    # I will duplicate the mapping logic here or try to import it carefully.
    
    # Let's verify mapping from main.py
    # DB_MAP in main.py:
    # 'emisor': 'Emisor'
    # ...
    
    # We will use the reverse logic: App Key -> DB Column
    # I'll copy the mapping here.
    
    DB_MAP = {
        'emisor': 'Emisor',
        'hora_solicitud': 'Hora Solicitud',
        'fecha': 'Fecha',
        'hotel': 'Hotel',
        'habitacion': 'Habitacion',
        'estado': 'Estado',
        'paciente': 'Paciente',
        'edad': 'Edad',
        'historia_medica': 'Historia Medica',
        'nacionalidad': 'Nacionalidad',
        'motivo_urgencia': 'Motivo Urgencia',
        'pagador': 'Pagador',
        'seguro': 'Seguro',
        'touroperador': 'Touroperador',
        'hora_aviso': 'Hora Aviso',
        'hora_finalizacion': 'Hora Finalización',
        'medico': 'Medico',
        'diagnostico': 'Diagnostico',
        'traslado': 'Traslado',
        'tipo_traslado': 'Tipo Traslado',
        'hora_ambulancia': 'Hora Ambulancia',
        'ingreso': 'Ingreso',
        'medico_ingreso': 'Medico Ingreso',
        'observaciones': 'Observaciones'
    }
    APP_MAP = {v: k for k, v in DB_MAP.items()}

    inserted_count = 0
    for row in data:
        cols = []
        vals = []
        params = []
        
        for app_key, val in row.items():
            if app_key in APP_MAP:
                cols.append(APP_MAP[app_key])
                vals.append("%s")
                params.append(str(val))
        
        if cols:
            query = f"INSERT INTO avisos ({','.join(cols)}) VALUES ({','.join(vals)})"
            res = db.execute_query(query, tuple(params))
            if res is not None:
                inserted_count += 1
                
    print(f"Migration completed. Inserted {inserted_count} records.")

if __name__ == "__main__":
    migrate()
