"""
Script de prueba para verificar la carga de avisos desde la base de datos
"""
import sys
import os

# Añadir el directorio actual al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import db

# Mapeo de columnas
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

def test_load_avisos():
    print("=" * 60)
    print("TEST: Carga de Avisos desde Base de Datos")
    print("=" * 60)
    
    # Conectar a la base de datos
    if not db.connect():
        print("❌ ERROR: No se pudo conectar a la base de datos")
        return
    
    print("✓ Conexión a base de datos exitosa")
    
    # Ejecutar query
    try:
        rows = db.execute_query("SELECT * FROM avisos ORDER BY id ASC")
        
        if rows is None:
            print("❌ ERROR: La query retornó None")
            return
        
        print(f"✓ Query ejecutada exitosamente")
        print(f"✓ Total de avisos encontrados: {len(rows)}")
        print()
        
        if len(rows) == 0:
            print("⚠️  No hay avisos en la base de datos")
            return
        
        # Procesar los avisos
        data = []
        for idx, r in enumerate(rows):
            item = {}
            # Map DB columns to App keys
            for db_col, app_key in DB_MAP.items():
                item[app_key] = r.get(db_col, "")
            
            # Preserve ID and other metadata
            item['_id'] = r['id'] 
            item['created_at'] = r.get('created_at')
            data.append(item)
            
            # Mostrar primeros 3 avisos
            if idx < 3:
                print(f"\n--- Aviso {idx + 1} ---")
                print(f"ID: {item['_id']}")
                print(f"Paciente: {item['Paciente']}")
                print(f"Hotel: {item['Hotel']}")
                print(f"Estado: {item['Estado']}")
                print(f"Fecha: {item['Fecha']}")
                print(f"Médico: {item['Medico']}")
        
        print()
        print("=" * 60)
        print(f"✓ ÉXITO: Se cargaron {len(data)} avisos correctamente")
        print("=" * 60)
        
        # Verificar que todos tienen los campos necesarios
        print("\nVerificando campos obligatorios...")
        for idx, aviso in enumerate(data[:3]):
            print(f"\nAviso {idx + 1}:")
            print(f"  - Tiene 'Paciente': {'Paciente' in aviso}")
            print(f"  - Tiene 'Hotel': {'Hotel' in aviso}")
            print(f"  - Tiene 'Estado': {'Estado' in aviso}")
            print(f"  - Tiene 'Fecha': {'Fecha' in aviso}")
            print(f"  - Valor Paciente: '{aviso.get('Paciente', 'N/A')}'")
            print(f"  - Valor Hotel: '{aviso.get('Hotel', 'N/A')}'")
        
    except Exception as e:
        print(f"❌ ERROR durante la carga: {e}")
        import traceback
        traceback.print_exc()
    
    db.close()

if __name__ == "__main__":
    test_load_avisos()
