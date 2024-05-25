'''
 * Nombre: DataGenerator.py
 * Autores:
    - Fernanda Esquivel, 21542
    - Adrian Fulladolsa, 21592
    - Elías Alvarado, 21808
 * Descripción: Programa para generar el dataset inicial.
 * Lenguaje: Python
 * Recursos: VSCode, JSON
 * Historial: 
    - Creado el 20.05.2024
    - Modificado el 24.05.2024
'''

import json
import os
import uuid
import random
from datetime import datetime, timedelta
from faker import Faker

#Configuración
seed = 288
numRows = 10
outputFile = "tables/schedules.json"

#Inicializar Faker y establecer semilla
faker = Faker()
random.seed(seed)
Faker.seed(seed)

# Arrays para los datos
edificios = ['A', 'C', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'CIT']
facultades = [
    "Educacion",
    "Ingenieria",
    "Ciencias y Humanidades",
    "Ciencias Sociales",
    "Design Innovations & Arts",
    "Business and Management",
    "Arquitectura"
]

#Generar datos de la tabla
metadata = {
    "table_name": "schedules",
    "column_families": [
        "classrooms",
        "teachers"
    ],
    "disabled": False,
    "created": datetime.now().isoformat(),
    "modified": datetime.now().isoformat(),
    "versions": 3
}

rows_data = {}

#Función para generar timestamps aleatorios
def random_timestamps(n):
    base_time = datetime.now()
    return [(base_time - timedelta(days=random.randint(0, 30))).isoformat() for _ in range(n)]

#Generar filas
for _ in range(numRows):
    row_id = str(uuid.uuid4())
    classrooms = {
        "identifier": {ts: f"{random.choice(edificios)}-{random.randint(100, 999)}" for ts in random_timestamps(random.randint(1, 3))},
        "capacity": {ts: str(random.randint(20, 50)) for ts in random_timestamps(random.randint(1, 3))},
        "type": {ts: faker.word(ext_word_list=["aula", "laboratorio", "aula colaborativa", "salon"]) for ts in random_timestamps(random.randint(1, 3))}
    }
    teachers = {
        "name": {ts: faker.name() for ts in random_timestamps(random.randint(1, 3))},
        "faculty": {ts: random.choice(facultades) for ts in random_timestamps(random.randint(1, 3))}
    }
    rows_data[row_id] = {
        "classrooms": classrooms,
        "teachers": teachers
    }

#Estructura completa de la tabla
schedules_table = {
    "metadata": metadata,
    "rows_data": rows_data
}

#Verificar si el archivo existe
if os.path.exists(outputFile):
    overwrite = input(f"El archivo {outputFile} ya existe. ¿Desea sobrescribirlo? (s/n): ").strip().lower()
    if overwrite != 's':
        print("Operación cancelada.")
        exit()

#Guardar los datos en el archivo JSON
with open(outputFile, 'w') as f:
    json.dump(schedules_table, f, indent=4)

print(f"Archivo {outputFile} generado con {numRows} filas.")
