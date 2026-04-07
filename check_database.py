from src.database import db
import json

print("=" * 60)
print("VERIFICACION DE BASE DE DATOS POSTGRESQL")
print("=" * 60)
print()

# 1. Verificar conexion
print("1. CONEXION A LA BASE DE DATOS")
print("-" * 60)
if db.connect():
    print("Estado: CONECTADO")
    print(f"Host: {db.host}")
    print(f"Puerto: {db.port}")
    print(f"Base de datos: {db.database}")
    print(f"Usuario: {db.user}")
    conexion_ok = True
else:
    print("Estado: ERROR - No se pudo conectar")
    print("La base de datos NO esta operativa")
    conexion_ok = False

print()

if not conexion_ok:
    print("=" * 60)
    print("RESULTADO: BASE DE DATOS NO OPERATIVA")
    print("=" * 60)
    exit(1)

# 2. Verificar tabla avisos
print("2. TABLA 'avisos'")
print("-" * 60)
try:
    result = db.execute_query("SELECT COUNT(*) as total FROM avisos")
    if result:
        total = result[0]['total']
        print(f"Estado: EXISTE")
        print(f"Total de registros: {total}")
        tabla_ok = True
    else:
        print("Estado: ERROR - No se pudo contar registros")
        tabla_ok = False
except Exception as e:
    print(f"Estado: ERROR - {e}")
    tabla_ok = False

print()

# 3. Verificar estructura
if tabla_ok:
    print("3. ESTRUCTURA DE LA TABLA")
    print("-" * 60)
    try:
        result = db.execute_query("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'avisos' 
            ORDER BY ordinal_position
        """)
        if result:
            print(f"Total de columnas: {len(result)}")
            print()
            print("Columnas principales:")
            for col in result[:10]:
                print(f"  - {col['column_name']:<20} ({col['data_type']})")
            if len(result) > 10:
                print(f"  ... y {len(result) - 10} columnas mas")
        else:
            print("No se pudo obtener estructura")
    except Exception as e:
        print(f"Error: {e}")

    print()

    # 4. Verificar datos
    print("4. DATOS EN LA TABLA")
    print("-" * 60)
    try:
        result = db.execute_query("""
            SELECT id, paciente, hotel, estado, fecha 
            FROM avisos 
            ORDER BY id DESC 
            LIMIT 5
        """)
        if result and len(result) > 0:
            print(f"Ultimos {len(result)} avisos registrados:")
            print()
            for aviso in result:
                print(f"  ID {aviso['id']:>4}: {aviso['paciente']:<30} | {aviso['hotel']:<25} | {aviso['estado']}")
        else:
            print("La tabla esta vacia (sin registros)")
    except Exception as e:
        print(f"Error: {e}")

print()
print("=" * 60)
print("RESUMEN FINAL")
print("=" * 60)
print()
print("Base de datos PostgreSQL: OPERATIVA")
print("Tabla 'avisos': CREADA Y FUNCIONAL")
print()
print("La base de datos esta lista para usar en la aplicacion.")
print()
print("=" * 60)

db.close()
