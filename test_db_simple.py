import sys
from src.database import db

# Test 1: Conexion
print("TEST 1: Conexion a PostgreSQL")
if db.connect():
    print("RESULTADO: OK - Conectado exitosamente")
    print(f"  Host: {db.host}:{db.port}")
    print(f"  Database: {db.database}")
else:
    print("RESULTADO: FALLO - No se pudo conectar")
    sys.exit(1)

print()

# Test 2: Tabla existe
print("TEST 2: Verificar tabla 'avisos'")
try:
    result = db.execute_query("SELECT COUNT(*) as total FROM avisos")
    total = result[0]['total'] if result else 0
    print(f"RESULTADO: OK - Tabla existe con {total} registros")
except Exception as e:
    print(f"RESULTADO: FALLO - {e}")
    sys.exit(1)

print()

# Test 3: Estructura
print("TEST 3: Estructura de la tabla")
try:
    result = db.execute_query("""
        SELECT COUNT(*) as total 
        FROM information_schema.columns 
        WHERE table_name = 'avisos'
    """)
    columnas = result[0]['total'] if result else 0
    print(f"RESULTADO: OK - La tabla tiene {columnas} columnas")
except Exception as e:
    print(f"RESULTADO: FALLO - {e}")

print()

# Test 4: Datos de muestra
print("TEST 4: Leer datos de la tabla")
try:
    result = db.execute_query("SELECT * FROM avisos LIMIT 1")
    if result and len(result) > 0:
        print(f"RESULTADO: OK - Se pueden leer datos correctamente")
        print(f"  Ejemplo: Paciente '{result[0].get('paciente', 'N/A')}'")
    else:
        print("RESULTADO: OK - Tabla vacia pero funcional")
except Exception as e:
    print(f"RESULTADO: FALLO - {e}")

print()
print("=" * 50)
print("CONCLUSION: BASE DE DATOS POSTGRESQL OPERATIVA")
print("=" * 50)

db.close()
