"""
Script para cargar avisos de prueba en la base de datos
"""
from src.database import db
from datetime import datetime, timedelta
import random

# Datos de ejemplo
hoteles = [
    "Amare Marbella Beach Hotel",
    "Hotel Don Carlos",
    "Hard Rock Hotel Marbella",
    "Kempinski Hotel Bahía",
    "Puente Romano Beach Resort",
    "Los Monteros Spa & Golf Resort",
    "Guadalpin Banús Hotel",
    "Hotel Fuerte Marbella"
]

medicos = [
    "Dr. García López",
    "Dra. Martínez Ruiz",
    "Dr. Fernández Sánchez",
    "Dra. Rodríguez Pérez",
    "Dr. López Hernández"
]

nacionalidades = ["Española", "Británica", "Alemana", "Francesa", "Italiana", "Holandesa"]
pagadores = ["Seguro Privado", "Particular", "Touroperador", "Seguro Viaje"]
seguros = ["Sanitas", "Adeslas", "AXA", "Mapfre", "Asisa", "DKV"]
touroperadores = ["TUI", "Thomas Cook", "Jet2holidays", "Loveholidays", ""]

motivos = [
    "Dolor abdominal agudo",
    "Fiebre alta y malestar general",
    "Traumatismo en extremidad",
    "Dificultad respiratoria",
    "Cefalea intensa",
    "Dolor torácico",
    "Reacción alérgica",
    "Gastroenteritis aguda"
]

diagnosticos = [
    "Gastroenteritis aguda - Tratamiento sintomático",
    "Infección respiratoria alta - Antibiótico prescrito",
    "Esguince tobillo derecho - Reposo y antiinflamatorios",
    "Migraña - Analgesia y observación",
    "Angina de pecho - Derivado a cardiología",
    "Urticaria - Antihistamínicos",
    "Cólico nefrítico - Analgesia y hidratación",
    "Faringitis aguda - Tratamiento sintomático"
]

def generar_avisos_prueba():
    """Genera 10 avisos de prueba con datos realistas"""
    
    print("Conectando a la base de datos...")
    if not db.connect():
        print("ERROR: No se pudo conectar a la base de datos")
        return
    
    print("Inicializando esquema de base de datos...")
    db.initialize_db()
    
    print("\nGenerando 10 avisos de prueba...")
    
    fecha_base = datetime.now()
    
    for i in range(10):
        # Alternar entre abiertos y cerrados
        estado = "Cerrado" if i % 3 == 0 else "Abierto"
        
        # Generar fecha de hoy
        fecha = fecha_base.strftime("%d/%m/%Y")
        hora_solicitud = f"{random.randint(8, 22):02d}:{random.randint(0, 59):02d}"
        hora_aviso = f"{random.randint(8, 22):02d}:{random.randint(0, 59):02d}"
        
        # Datos del aviso
        aviso = {
            "emisor": random.choice(["Recepción", "Enfermería", "Urgencias"]),
            "hora_solicitud": hora_solicitud,
            "fecha": fecha,
            "hotel": random.choice(hoteles),
            "habitacion": f"{random.randint(100, 999)}",
            "estado": estado,
            "paciente": f"Paciente {i+1}",
            "edad": str(random.randint(25, 75)),
            "historia_medica": f"HM{random.randint(10000, 99999)}",
            "nacionalidad": random.choice(nacionalidades),
            "motivo_urgencia": random.choice(motivos),
            "pagador": random.choice(pagadores),
            "seguro": random.choice(seguros),
            "touroperador": random.choice(touroperadores),
            "hora_aviso": hora_aviso,
            "medico": random.choice(medicos),
            "diagnostico": random.choice(diagnosticos) if estado == "Cerrado" else "",
            "traslado": random.choice(["Sí", "No"]),
            "observaciones": f"Observaciones del aviso {i+1}"
        }
        
        # Si está cerrado, añadir hora de finalización
        if estado == "Cerrado":
            hora_fin = int(hora_aviso.split(":")[0]) + random.randint(1, 3)
            min_fin = random.randint(0, 59)
            aviso["hora_finalizacion"] = f"{hora_fin:02d}:{min_fin:02d}"
        else:
            aviso["hora_finalizacion"] = ""
        
        # Si hay traslado, añadir detalles
        if aviso["traslado"] == "Sí":
            aviso["tipo_traslado"] = random.choice(["Ambulancia", "Helicóptero", "Vehículo propio"])
            hora_amb = int(hora_aviso.split(":")[0]) + 1
            aviso["hora_ambulancia"] = f"{hora_amb:02d}:{random.randint(0, 59):02d}"
            aviso["ingreso"] = random.choice(["Sí", "No"])
            if aviso["ingreso"] == "Sí":
                aviso["medico_ingreso"] = random.choice(medicos)
            else:
                aviso["medico_ingreso"] = ""
        else:
            aviso["tipo_traslado"] = ""
            aviso["hora_ambulancia"] = ""
            aviso["ingreso"] = "No"
            aviso["medico_ingreso"] = ""
        
        # Insertar en la base de datos
        query = """
            INSERT INTO avisos (
                emisor, hora_solicitud, fecha, hotel, habitacion, estado,
                paciente, edad, historia_medica, nacionalidad, motivo_urgencia,
                pagador, seguro, touroperador, hora_aviso, hora_finalizacion,
                medico, diagnostico, traslado, tipo_traslado, hora_ambulancia,
                ingreso, medico_ingreso, observaciones
            ) VALUES (
                %(emisor)s, %(hora_solicitud)s, %(fecha)s, %(hotel)s, %(habitacion)s, %(estado)s,
                %(paciente)s, %(edad)s, %(historia_medica)s, %(nacionalidad)s, %(motivo_urgencia)s,
                %(pagador)s, %(seguro)s, %(touroperador)s, %(hora_aviso)s, %(hora_finalizacion)s,
                %(medico)s, %(diagnostico)s, %(traslado)s, %(tipo_traslado)s, %(hora_ambulancia)s,
                %(ingreso)s, %(medico_ingreso)s, %(observaciones)s
            )
        """
        
        result = db.execute_query(query, aviso)
        
        if result is not None:
            print(f"✓ Aviso {i+1} creado: {aviso['paciente']} - {aviso['hotel']} - Estado: {estado}")
        else:
            print(f"✗ Error al crear aviso {i+1}")
    
    print("\n¡Proceso completado!")
    print("Reinicia la aplicación para ver los avisos cargados.")
    db.close()

if __name__ == "__main__":
    generar_avisos_prueba()
