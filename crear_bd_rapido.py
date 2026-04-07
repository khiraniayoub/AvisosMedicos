import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

print("=" * 50)
print("CREANDO BASE DE DATOS POSTGRESQL")
print("=" * 50)
print()

# Intentar diferentes puertos
puertos = ["5432", "5433", "5434"]
host = "localhost"
user = "postgres"
password = "1234"

conn_exitosa = None
puerto_exitoso = None

for puerto in puertos:
    try:
        print(f"Intentando conectar en puerto {puerto}...")
        conn = psycopg2.connect(
            host=host,
            port=puerto,
            user=user,
            password=password,
            database="postgres",
            connect_timeout=3
        )
        conn_exitosa = conn
        puerto_exitoso = puerto
        print(f"   ✓ Conectado en puerto {puerto}")
        break
    except Exception as e:
        print(f"   ✗ Puerto {puerto}: {str(e)[:50]}")

if not conn_exitosa:
    print()
    print("=" * 50)
    print("✗ NO SE PUDO CONECTAR A POSTGRESQL")
    print("=" * 50)
    print()
    print("Posibles soluciones:")
    print("1. Verifica la contraseña en pgAdmin")
    print("2. Verifica el puerto en pgAdmin")
    print("3. Reinicia el servicio PostgreSQL")
    exit(1)

print()

try:
    conn_exitosa.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn_exitosa.cursor()
    
    # Crear base de datos
    print("2. Creando base de datos 'avisos_db'...")
    try:
        cursor.execute("CREATE DATABASE avisos_db;")
        print("   ✓ Base de datos creada")
    except psycopg2.errors.DuplicateDatabase:
        print("   ⚠ Base de datos ya existe (OK)")
    except Exception as e:
        print(f"   ⚠ {e}")
    print()
    
    cursor.close()
    conn_exitosa.close()
    
    # Conectar a la nueva base de datos
    print("3. Conectando a 'avisos_db'...")
    conn = psycopg2.connect(
        host=host,
        port=puerto_exitoso,
        user=user,
        password=password,
        database="avisos_db"
    )
    cursor = conn.cursor()
    print("   ✓ Conectado a avisos_db")
    print()
    
    # Crear tabla
    print("4. Creando tabla 'avisos'...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS avisos (
            id SERIAL PRIMARY KEY,
            emisor VARCHAR(255),
            hora_solicitud VARCHAR(50),
            fecha VARCHAR(50),
            hotel VARCHAR(255),
            habitacion VARCHAR(50),
            estado VARCHAR(50),
            paciente VARCHAR(255),
            edad VARCHAR(50),
            historia_medica TEXT,
            nacionalidad VARCHAR(100),
            motivo_urgencia TEXT,
            pagador VARCHAR(100),
            seguro VARCHAR(100),
            touroperador VARCHAR(100),
            hora_aviso VARCHAR(50),
            hora_finalizacion VARCHAR(50),
            medico VARCHAR(255),
            diagnostico TEXT,
            traslado VARCHAR(50),
            tipo_traslado VARCHAR(100),
            hora_ambulancia VARCHAR(50),
            ingreso VARCHAR(50),
            medico_ingreso VARCHAR(255),
            observaciones TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    print("   ✓ Tabla creada")
    print()
    
    # Crear índices
    print("5. Creando índices...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_avisos_fecha ON avisos(fecha);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_avisos_estado ON avisos(estado);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_avisos_hotel ON avisos(hotel);")
    conn.commit()
    print("   ✓ Índices creados")
    print()
    
    # Verificar
    cursor.execute("SELECT COUNT(*) FROM avisos;")
    count = cursor.fetchone()[0]
    print(f"6. Verificación: Tabla tiene {count} registros")
    print()
    
    cursor.close()
    conn.close()
    
    print("=" * 50)
    print("✓ BASE DE DATOS CONFIGURADA EXITOSAMENTE")
    print("=" * 50)
    print()
    print(f"Puerto usado: {puerto_exitoso}")
    print()
    print("ACTUALIZA tu archivo .env con:")
    print(f"DB_PORT={puerto_exitoso}")
    print()
    print("Luego ejecuta: python src/migrate_csv_to_db.py")
    print()
    
except Exception as e:
    print(f"✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
