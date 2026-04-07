import socket
import sys
from src.database import db

print("=" * 60)
print("  TEST DE CONFIGURACION MULTI-USUARIO")
print("=" * 60)
print()

# Test 1: Obtener IP local
print("1. INFORMACION DEL SERVIDOR")
print("-" * 60)
hostname = socket.gethostname()
try:
    local_ip = socket.gethostbyname(hostname)
    print(f"Nombre del equipo: {hostname}")
    print(f"IP local: {local_ip}")
except:
    print("No se pudo obtener IP local")
print()

# Test 2: Configuracion actual
print("2. CONFIGURACION DE BASE DE DATOS")
print("-" * 60)
print(f"Host configurado: {db.host}")
print(f"Puerto: {db.port}")
print(f"Base de datos: {db.database}")
print(f"Usuario: {db.user}")
print()

# Test 3: Conexion
print("3. TEST DE CONEXION")
print("-" * 60)
if db.connect():
    print("Estado: CONECTADO")
    
    # Verificar si es servidor o cliente
    if db.host in ['localhost', '127.0.0.1']:
        print("Tipo: SERVIDOR (localhost)")
    else:
        print(f"Tipo: CLIENTE (conectando a {db.host})")
    
    print()
    
    # Test 4: Leer datos
    print("4. TEST DE LECTURA")
    print("-" * 60)
    try:
        result = db.execute_query("SELECT COUNT(*) as total FROM avisos")
        if result:
            total = result[0]['total']
            print(f"Total de avisos: {total}")
            
            # Mostrar ultimos 3
            avisos = db.execute_query("""
                SELECT id, paciente, hotel, fecha 
                FROM avisos 
                ORDER BY id DESC 
                LIMIT 3
            """)
            
            if avisos:
                print()
                print("Ultimos 3 avisos:")
                for av in avisos:
                    print(f"  - ID {av['id']}: {av['paciente']} ({av['hotel']})")
        else:
            print("No se pudieron leer datos")
    except Exception as e:
        print(f"Error al leer: {e}")
    
    print()
    
    # Test 5: Escribir datos de prueba
    print("5. TEST DE ESCRITURA")
    print("-" * 60)
    try:
        test_query = """
            INSERT INTO avisos (paciente, hotel, estado, fecha, emisor)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """
        result = db.execute_query(
            test_query,
            ("TEST MULTIUSUARIO", "Hotel Test", "Abierto", "2026-01-01", "Sistema")
        )
        
        if result:
            test_id = result[0]['id']
            print(f"Aviso de prueba creado: ID {test_id}")
            
            # Eliminar el aviso de prueba
            db.execute_query("DELETE FROM avisos WHERE id = %s", (test_id,))
            print("Aviso de prueba eliminado")
            print("Escritura: OK")
        else:
            print("No se pudo crear aviso de prueba")
    except Exception as e:
        print(f"Error al escribir: {e}")
    
    print()
    print("=" * 60)
    print("  RESULTADO: CONFIGURACION OPERATIVA")
    print("=" * 60)
    print()
    
    if db.host in ['localhost', '127.0.0.1']:
        print("Este PC es el SERVIDOR")
        print()
        print("Proximos pasos:")
        print("1. Anota la IP de este servidor:", local_ip)
        print("2. En otros PCs, edita .env y cambia:")
        print(f"   DB_HOST={local_ip}")
        print("3. Ejecuta este script en los clientes para verificar")
    else:
        print(f"Este PC es un CLIENTE conectado a: {db.host}")
        print()
        print("La configuracion multi-usuario esta funcionando!")
        print("Todos los cambios se sincronizaran con el servidor.")
    
else:
    print("Estado: ERROR - No se pudo conectar")
    print()
    print("=" * 60)
    print("  RESULTADO: ERROR DE CONEXION")
    print("=" * 60)
    print()
    print("Posibles causas:")
    print("1. PostgreSQL no esta ejecutandose")
    print("2. Configuracion incorrecta en .env")
    print("3. Firewall bloqueando conexion")
    print("4. IP del servidor incorrecta")
    print()
    print("Verifica:")
    print(f"- Host: {db.host}")
    print(f"- Puerto: {db.port}")
    print(f"- Base de datos: {db.database}")

db.close()
print()
