import csv
import random
from datetime import datetime, timedelta

# Listas de datos ficticios
emisores = ["Jaime", "Guia", "Paciente", "Seguro", "SMCS", "VITHAS", "RECEPCION", "GP"]
estados = ["Abierto", "Cerrado", "Anulado"]
hoteles = [
    "Gran Hotel Miramar GL (Malaga)",
    "BYPILLOW California",
    "Hotel Claude (Marbella)",
    "Casa Diez (Estepona)",
    "Amanhavis Hotel (Benahavis)",
    "El Fuerte Marbella",
    "Melia Costa Del Sol",
    "Catalonia Málaga",
    "Eurostars Oasis Marbella",
    "Casa la Concha (Marbella)",
    "VITHAS BENALMADENA",
    "Iberostar Malaga Playa",
    "Hotel Guadalmina Spa & Golf Resort",
    "Vincci Selección Aleysa",
    "Don Carlos Resort & Spa",
    "Marriott's Playa Andaluza",
    "Kempinski Hotel Bahía",
    "Puente Romano Beach Resort"
]

nombres = [
    "Juan García López", "María Rodríguez Martín", "Peter Schmidt", "Anna Müller",
    "John Smith", "Emma Johnson", "Pierre Dubois", "Sophie Martin",
    "Marco Rossi", "Giulia Ferrari", "Lars Andersson", "Ingrid Johansson",
    "Ahmed Hassan", "Fatima Ali", "Vladimir Petrov", "Natasha Ivanova",
    "Carlos Santos", "Ana Silva", "Michael Brown", "Sarah Wilson",
    "David Taylor", "Laura Anderson", "Thomas White", "Jessica Harris",
    "Daniel Martin", "Elena Garcia", "Robert Lee", "Patricia Clark",
    "James Lewis", "Linda Walker", "Christopher Hall", "Barbara Allen",
    "Matthew Young", "Susan King", "Anthony Wright", "Karen Scott",
    "Mark Green", "Nancy Adams", "Paul Baker", "Lisa Nelson"
]

nacionalidades = [
    "Español/a", "Alemán/a", "Británico/a", "Francés/a", "Italiano/a",
    "Sueco/a", "Noruego/a", "Holandés/a", "Belga", "Suizo/a",
    "Estadounidense", "Canadiense", "Australiano/a", "Ruso/a", "Polaco/a"
]

motivos = [
    "dolor de estomago", "fiebre alta", "dolor de cabeza intenso",
    "mareos y vómitos", "dolor en el pecho", "dificultad respiratoria",
    "caída con traumatismo", "reacción alérgica", "dolor abdominal",
    "lesión deportiva", "quemadura solar grave", "intoxicación alimentaria",
    "dolor de espalda", "torcedura de tobillo", "corte profundo"
]

pagadores = ["Paciente", "Seguro", "TTOO", "Hotel"]
seguros = [
    "Falck TravelCare", "Bupa Global", "Cigna Global", "Allianz Worldwide Care",
    "AXA Global Healthcare", "IMG Global", "GeoBlue", "Seven Corners"
]

touroperadores = [
    "TUI", "Alltours", "FTI Touristik", "Expedia", "Booking.com",
    "Thomas Cook", "Jet2holidays", "Neckermann", "DER Touristik"
]

medicos = [
    "Dr. Juan Pérez", "Dr. Elizabeth Blackwell", "Dr. Louis Pasteur",
    "Dr. Edward Jenner", "Dr. Joseph Lister", "Dr. Jonas Salk",
    "Dr. Hippocrates", "Dr. Galen", "Dr. Antonio García", "Dr. RANIA",
    "Dr. fidalgo", "Dr. María López", "Dr. Carlos Ruiz"
]

diagnosticos = [
    "GEA", "Gastroenteritis aguda", "Cefalea tensional", "Migraña",
    "Bronquitis aguda", "Faringitis", "Otitis media", "Conjuntivitis",
    "Lumbalgia", "Esguince de tobillo", "Contusión", "Dermatitis",
    "Cistitis", "Ansiedad", "Insolación", "Deshidratación"
]

tipos_traslado = ["Ambulancias Andalucia", "Ambulancias AGP", "Helicopteros Sanitarios", "Medios Propios"]
ingresos = ["No ingresa", "Planta", "UCI"]

# Generar fechas de los últimos 10 días
fecha_fin = datetime.now()
fecha_inicio = fecha_fin - timedelta(days=10)

# Leer avisos existentes
avisos_existentes = []
try:
    with open('avisos.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        avisos_existentes = list(reader)
except FileNotFoundError:
    pass

# Generar 40 nuevos avisos
nuevos_avisos = []
for i in range(40):
    # Fecha aleatoria en los últimos 10 días
    dias_atras = random.randint(0, 10)
    fecha = (fecha_fin - timedelta(days=dias_atras)).strftime("%Y-%m-%d")
    
    # Hora aleatoria
    hora = f"{random.randint(8, 23):02d}:{random.randint(0, 59):02d}"
    
    # Estado con más cerrados que abiertos
    estado = random.choices(estados, weights=[15, 70, 15])[0]
    
    # Datos del aviso
    emisor = random.choice(emisores)
    hotel = random.choice(hoteles)
    habitacion = str(random.randint(100, 999)) if random.random() > 0.3 else ""
    paciente = random.choice(nombres)
    edad = random.randint(18, 85)
    nhc = str(random.randint(10000000, 99999999)) if random.random() > 0.5 else ""
    nacionalidad = random.choice(nacionalidades)
    motivo = random.choice(motivos)
    
    pagador = random.choice(pagadores)
    seguro = random.choice(seguros) if pagador == "Seguro" else ""
    ttoo = random.choice(touroperadores) if random.random() > 0.3 else ""
    
    medico = random.choice(medicos) if estado == "Cerrado" else ""
    diagnostico = random.choice(diagnosticos) if estado == "Cerrado" else ""
    
    # Traslado
    requiere_traslado = random.choice(["Si", "No"])
    tipo_traslado = random.choice(tipos_traslado) if requiere_traslado == "Si" else ""
    hora_ambulancia = f"{random.randint(8, 23):02d}:{random.randint(0, 59):02d}" if requiere_traslado == "Si" else ""
    
    # Ingreso
    ingreso = random.choice(ingresos)
    medico_ingreso = random.choice(medicos) if ingreso != "No ingresa" else ""
    
    hora_fin = f"{random.randint(int(hora.split(':')[0]), 23):02d}:{random.randint(0, 59):02d}" if estado == "Cerrado" else ""
    
    observaciones = ""
    
    aviso = {
        "Emisor": emisor,
        "Hora Solicitud": hora,
        "Fecha": fecha,
        "Hotel": hotel,
        "Habitacion": habitacion,
        "Estado": estado,
        "Paciente": paciente,
        "Edad": str(edad),
        "Historia Medica": nhc,
        "Nacionalidad": nacionalidad,
        "Motivo Urgencia": motivo,
        "Pagador": pagador,
        "Seguro": seguro,
        "Touroperador": ttoo,
        "Hora Aviso": hora,
        "Hora Finalización": hora_fin,
        "Medico": medico,
        "Diagnostico": diagnostico,
        "Traslado": requiere_traslado,
        "Tipo Traslado": tipo_traslado,
        "Hora Ambulancia": hora_ambulancia,
        "Ingreso": ingreso,
        "Medico Ingreso": medico_ingreso,
        "Observaciones": observaciones
    }
    
    nuevos_avisos.append(aviso)

# Combinar avisos existentes con nuevos
todos_avisos = avisos_existentes + nuevos_avisos

# Guardar en el archivo CSV
fieldnames = [
    "Emisor", "Hora Solicitud", "Fecha", "Hotel", "Habitacion", "Estado",
    "Paciente", "Edad", "Historia Medica", "Nacionalidad", "Motivo Urgencia",
    "Pagador", "Seguro", "Touroperador", "Hora Aviso", "Hora Finalización",
    "Medico", "Diagnostico", "Traslado", "Tipo Traslado", "Hora Ambulancia",
    "Ingreso", "Medico Ingreso", "Observaciones"
]

with open('avisos.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(todos_avisos)

print(f"✅ Se han generado {len(nuevos_avisos)} avisos ficticios")
print(f"📊 Total de avisos en el sistema: {len(todos_avisos)}")
print(f"📅 Fechas: desde {fecha_inicio.strftime('%Y-%m-%d')} hasta {fecha_fin.strftime('%Y-%m-%d')}")
