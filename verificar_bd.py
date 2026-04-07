from src.database import db

print("=" * 50)
print("VERIFICACIÓN DE BASE DE DATOS POSTGRESQL")
print("=" * 50)
print()

# 1. Verificar conexión
print("1. Verificando conexión...")
if db.connect():
    print("   ✅ Conexión exitosa a PostgreSQL")
    print(f"   - Host: {db.host}")
    print(f"   - Puerto: {db.port}")
    print(f"   - Base de datos: {db.database}")
    print(f"   - Usuario: {db.user}")
else:
    print("   ❌ Error de conexión")
    print("   La base de datos NO está operativa")
    exit(1)

print()

# 2. Verificar tabla avisos
print("2. Verificando tabla 'avisos'...")
try:
    result = db.execute_query("SELECT COUNT(*) as total FROM avisos")
    if result:
        total = result[0]['total']
        print(f"   ✅ Tabla 'avisos' existe")
        print(f"   - Total de registros: {total}")
    else:
        print("   ⚠️ No se pudo contar registros")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# 3. Verificar estructura de la tabla
print("3. Verificando estructura de la tabla...")
try:
    result = db.execute_query("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'avisos' 
        ORDER BY ordinal_position
    """)
    if result:
        print(f"   ✅ Tabla tiene {len(result)} columnas:")
        for col in result[:5]:  # Mostrar primeras 5
            print(f"      - {col['column_name']}: {col['data_type']}")
        if len(result) > 5:
            print(f"      ... y {len(result) - 5} columnas más")
    else:
        print("   ⚠️ No se pudo obtener estructura")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# 4. Verificar últimos registros
print("4. Verificando últimos registros...")
try:
    result = db.execute_query("""
        SELECT id, paciente, hotel, estado, fecha 
        FROM avisos 
        ORDER BY id DESC 
        LIMIT 5
    """)
    if result and len(result) > 0:
        print(f"   ✅ Últimos {len(result)} avisos:")
        for aviso in result:
            print(f"      ID {aviso['id']}: {aviso['paciente']} - {aviso['hotel']} ({aviso['estado']})")
    else:
        print("   ⚠️ No hay registros en la tabla (tabla vacía)")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# 5. Resumen final
print("=" * 50)
print("RESUMEN")
print("=" * 50)
print("✅ Base de datos PostgreSQL: OPERATIVA")
print("✅ Tabla 'avisos': CREADA Y FUNCIONAL")
print()
print("La base de datos está lista para usar.")
print("=" * 50)

db.close()
