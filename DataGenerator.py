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
    - Modificado el 20.05.2024
'''

# import time
# from datetime import datetime
# current_timestamp = time.time()
# dt_object = datetime.fromtimestamp(current_timestamp)
# print(dt_object)

# Colores ANSI
RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"

def print_colored(text, color):
    print(f"{color}{text}{RESET}")

if __name__ == "__main__":
    print_colored("Este es un texto en rojo", RED)
    print_colored("Este es un texto en verde", GREEN)
    print_colored("Este es un texto en amarillo", YELLOW)
    print_colored("Este es un texto en azul", BLUE)

import uuid

# Printing random id using uuid1() 
print ("The random id using uuid1() is : ",end="") 
print (uuid.uuid4()) 
