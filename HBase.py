'''
 * Nombre: HBase.py
 * Autores:
    - Fernanda Esquivel, 21542
    - Adrian Fulladolsa, 21592
    - Elías Alvarado, 21808
 * Descripción: Programa principal que simula el funcionamiento de una base de datos NoSQL tipo HBase.
 * Lenguaje: Python
 * Recursos: VSCode, JSON
 * Historial: 
    - Creado el 20.05.2024
    - Modificado el 24.05.2024
'''

import json
import os
from datetime import datetime
import pyfiglet
from rich.console import Console
from rich.style import Style
from prettytable import PrettyTable
import fnmatch
import uuid
import time
from tqdm import tqdm

#Definir consola y estilos de rich
console = Console()
magenta = Style(color="magenta", bold=True)
red = Style(color="red", bold=True)
blue = Style(color="blue", bold=True)
green = Style(color="green", bold=True)
yellow = Style(color="yellow", bold=True)

class HBase:
    """
    Constructor de la clase HBase
    """
    def __init__(self, directory='tables'):
        self.directory = directory
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    """
    Función para crear una tabla en HBase
    * fileName: Nombre del archivo JSON donde se guardará la tabla
    * tableName: Nombre de la tabla
    * columnFamilies: Lista de column families de la tabla
    """
    def create(self, fileName, tableName, columnFamilies, versions):
        #Definir la estructura de la tabla
        tableStructure = {
            "metadata": {
                "table_name": tableName,
                "column_families": columnFamilies,
                "disabled": False,
                "created": datetime.now().isoformat(),
                "modified": datetime.now().isoformat(),
                "versions": versions
                #"rows_counter": 0
            },
            "rows_data": {}
        }
        
        #Crear el archivo JSON con la estructura de la tabla
        filePath = os.path.join(self.directory, fileName)
        
        if os.path.exists(filePath):
            console.print(f"SISTEMA: El archivo {fileName} ya existe. ¿Desea sobrescribirlo? (s/n): ", style=blue)
            overwrite = input().strip().lower()
            if overwrite != 's':
                console.print("SISTEMA: Operación cancelada. La tabla no fue creada.", style=blue)
                return
        
        with open(filePath, 'w') as f:
            json.dump(tableStructure, f, indent=4)
        
        console.print(f'SISTEMA: Tabla {tableName} creada en {filePath}.', style=blue)
    
    """
    Función para listar las tablas en HBase
    """
    def list(self):
        listTable = PrettyTable()
        listTable.field_names = ["Tabla", "Column Families"]
        
        for file in os.listdir(self.directory):
            if file.endswith('.json'):
                tableName = file.replace('.json', '')
                filePath = os.path.join(self.directory, file)
                with open(filePath, 'r') as f:
                    data = json.load(f)
                    columnFamilies = ", ".join(data["metadata"]["column_families"])
                listTable.add_row([tableName, columnFamilies])
        
        print(listTable)
    
    """
    Función para deshabilitar una tabla en HBase
    * tableName: Nombre de la tabla a deshabilitar
    """
    def changeStatus(self, tableName, action):
        found = False
        for file in os.listdir(self.directory):
            if file.endswith('.json'):
                filePath = os.path.join(self.directory, file)
                with open(filePath, 'r') as f:
                    data = json.load(f)
                    if data["metadata"]["table_name"] == tableName:
                        if action == "disable":
                            data["metadata"]["disabled"] = True
                        elif action == "enable":
                            data["metadata"]["disabled"] = False
                        data["metadata"]["modified"] = datetime.now().isoformat()
                        found = True
                        with open(filePath, 'w') as f_write:
                            json.dump(data, f_write, indent=4)
                        if action == "disable":
                            console.print(f'SISTEMA: Tabla {tableName} deshabilitada.', style=blue)
                        elif action == "enable":
                            console.print(f'SISTEMA: Tabla {tableName} habilitada.', style=blue)
                        break
        
        if not found:
            print()
            console.print(f'ERROR: Tabla {tableName} no encontrada.', style=red)
            
    
    """
    Función para verificar si una tabla está habilitada o no
    * tableName: Nombre de la tabla a verificar
    """
    def is_enabled(self, tableName):
        found = False

        for file in os.listdir(self.directory):
            if file.endswith('.json'):
                filePath = os.path.join(self.directory, file)

                with open(filePath, 'r') as f:
                    data = json.load(f)

                    if data["metadata"]["table_name"] == tableName:
                        found = True
                        if data["metadata"]["disabled"]:
                            print(f'Table {tableName} IS disabled.')
                            console.print(f'Tabla {tableName} SI está deshabilitada.', style=yellow)
                        else:
                            console.print(f'Tabla {tableName} NO está deshabilitada.', style=green)
                        break
        
        if not found:
            console.print(f'ERROR: Tabla {tableName} no encontrada.', style=red)

    """
    Función para alterar una tabla en HBase
    * tableName: Nombre de la tabla a alterar
    * newTableName: Nuevo nombre de la tabla
    * newColumnFamilies: Nuevas column families de la tabla
    """
    def alter(self, tableName, newTableName, newColumnFamilies):
        found = False

        for file in os.listdir(self.directory):
            if file.endswith('.json'):
                filePath = os.path.join(self.directory, file)

                with open(filePath, 'r') as f:
                    data = json.load(f)

                    if data["metadata"]["table_name"] == tableName:
                        if data["metadata"]["disabled"]:
                            #Actualizar los metadatos de la tabla
                            data["metadata"]["table_name"] = newTableName
                            if newColumnFamilies != ['']:
                                data["metadata"]["column_families"] += newColumnFamilies
                            data["metadata"]["modified"] = datetime.now().isoformat()
                            found = True

                            #Guardar los cambios en el archivo JSON
                            with open(filePath, 'w') as f_write:
                                json.dump(data, f_write, indent=4)
                            
                            console.print(f"SISTEMA: Tabla {tableName} ha sido alterada a {newTableName} con nuevas column families.", style=blue)
                        else:
                            found = True
                            console.print(f'ERROR: Tabla {tableName} está habilitada y no puede ser alterada.', style=red)

                        break
        
        if not found:
            console.print(f'ERROR: Tabla {tableName} no encontrada.', style=red)

    """
    Función para eliminar una tabla en HBase
    * tableName: Nombre de la tabla a eliminar
    """
    def drop(self, tableName):
        found = False

        for file in os.listdir(self.directory):
            if file.endswith('.json'):
                file_path = os.path.join(self.directory, file)

                with open(file_path, 'r') as f:
                    data = json.load(f)

                if data["metadata"]["table_name"] == tableName:
                    found = True
                    if data["metadata"]["disabled"]:
                        try:
                            os.remove(file_path)
                            console.print(f"SISTEMA: Tabla {tableName} ha sido eliminada.", style=blue)
                        except PermissionError:
                            console.print(f'EROR: No se puede eliminar la tabla {tableName} pues el archivo está en uso.', style=red)
                    else:
                        console.print(f'ERROR: Tabla {tableName} está habilitada y no puede ser eliminada.', style=red)
                        break
        
        if not found:
            console.print(f'ERROR: Tabla {tableName} no encontrada.', style=red)

    """
    Función para eliminar todas las tablas que coincidan con un patrón
    * pattern: Patrón de las tablas a eliminar
    """
    def drop_all(self, pattern):
        found = False

        for file in os.listdir(self.directory):
            if file.endswith('.json'):
                file_path = os.path.join(self.directory, file)

                with open(file_path, 'r') as f:
                    data = json.load(f)
                tableName = data["metadata"]["table_name"]

                if fnmatch.fnmatch(tableName, pattern):
                    found = True
                    if data["metadata"]["disabled"]:
                        try:
                            os.remove(file_path)
                            console.print(f"SISTEMA: Tabla {tableName} ha sido eliminada.", style=blue)
                        except PermissionError:
                            console.print(f'EROR: No se puede eliminar la tabla {tableName} pues el archivo está en uso.', style=red)
                    else:
                        console.print(f'ERROR: Tabla {tableName} está habilitada y no puede ser eliminada.', style=red)

        if not found:
            console.print(f'ERROR: No se encontarton tablas que coindican con el patron "{pattern}".', style=red)
    
    """
    Función para describir una tabla en HBase
    * tableName: Nombre de la tabla a describir
    """
    def describe(self, tableName):
        found = False

        for file in os.listdir(self.directory):
            if file.endswith('.json'):
                file_path = os.path.join(self.directory, file)
                
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if data["metadata"]["table_name"] == tableName:
                        found = True
                        metadata = data["metadata"]
                        
                        table = PrettyTable()
                        table.field_names = ["Atributo", "Valor"]
                        
                        table.add_row(["Table Name", metadata["table_name"]])
                        table.add_row(["Column Families", ", ".join(metadata["column_families"])])
                        table.add_row(["Disabled", metadata["disabled"]])
                        table.add_row(["Created", metadata["created"]])
                        table.add_row(["Modified", metadata["modified"]])
                        table.add_row(["Versions", metadata.get("versions", "N/A")])
                        
                        print(table)
                        break
        
        if not found:
            console.print(f'ERROR: Tabla {tableName} no encontrada.', style=red)

    """
    Función para insertar o actualizar una fila dentro de una tabla en HBase
    * tableName: Nombre de la tabla
    * action: Acción a realizar (insertar o actualizar)
    """
    def put(self, tableName, action):
        found = False
        for file in os.listdir(self.directory):
            if file.endswith('.json'):
                filePath = os.path.join(self.directory, file)
                with open(filePath, 'r') as f:
                    data = json.load(f)
                
                if data["metadata"]["table_name"] == tableName:
                    data["metadata"]["modified"] = datetime.now().isoformat()
                    found = True
                    columnFamilies = data["metadata"]["column_families"]
                    versions = data["metadata"].get("versions", 3)  #Default to 3 if versions not specified

                    if action == 'i':
                        rowID = str(uuid.uuid4())
                        row_data = {}
                        for cf in columnFamilies:
                            cf_data = {}
                            print(f"Column Family: {cf}")
                            properties = input(f"Ingrese las propiedades para {cf} separadas por comas: ").strip().split(',')
                            for prop in properties:
                                value = input(f"Ingrese el valor para {prop}: ").strip()
                                timestamp = datetime.now().isoformat()
                                cf_data[prop] = {timestamp: value}
                            row_data[cf] = cf_data
                        data["rows_data"][rowID] = row_data
                        data["metadata"]["modified"] = datetime.now().isoformat()
                        #data["metadata"]["rows_counter"] += 1

                    elif action == 'u':
                        rowID = input("Ingrese el ID de la fila a actualizar: ").strip()
                        if rowID in data["rows_data"]:
                            for cf in columnFamilies:
                                if cf in data["rows_data"][rowID]:
                                    print(f"Column Family: {cf}")
                                    for prop in data["rows_data"][rowID][cf]:
                                        value = input(f"Ingrese el nuevo valor para {prop} (actual: {list(data['rows_data'][rowID][cf][prop].values())}): ").strip()
                                        timestamp = datetime.now().isoformat()
                                        if prop in data["rows_data"][rowID][cf]:
                                            #Limit the number of versions stored
                                            if len(data["rows_data"][rowID][cf][prop]) >= versions:
                                                oldest_timestamp = sorted(data["rows_data"][rowID][cf][prop])[0]
                                                del data["rows_data"][rowID][cf][prop][oldest_timestamp]
                                            data["rows_data"][rowID][cf][prop][timestamp] = value
                                        else:
                                            data["rows_data"][rowID][cf][prop] = {timestamp: value}
                            data["metadata"]["modified"] = datetime.now().isoformat()
                        else:
                            console.print(f"ERROR: No se encontró la fila con ID {rowID}.", style=red)
                    else:
                        console.print(f"Acción no válida. Use 'i' para insertar o 'u' para actualizar.", style=red)
                        return

                    #Guardar los cambios en el archivo JSON
                    with open(filePath, 'w') as f_write:
                        json.dump(data, f_write, indent=4)
                    console.print(f"SISTEMA: Operación realizada en la tabla {tableName}.", style=blue)
                    break
        
        if not found:
            console.print(f'ERROR: Tabla {tableName} no encontrada.', style=red)

    """
    Función para obtener los datos de una fila en una tabla de HBase
    * tableName: Nombre de la tabla
    * rowID: ID de la fila a obtener
    """
    def get(self, tableName, rowID):
        foundTable = False
        foundRow = False
        
        for file in os.listdir(self.directory):
            if file.endswith('.json'):
                filePath = os.path.join(self.directory, file)
                with open(filePath, 'r') as f:
                    data = json.load(f)
                
                if data["metadata"]["table_name"] == tableName:
                    foundTable = True
                    if rowID in data["rows_data"]:
                        foundRow = True
                        rowData = data["rows_data"][rowID]
                        
                        table = PrettyTable()
                        headers = ["Row key"]
                        row = [rowID]
                        
                        for cf, properties in rowData.items():
                            for prop, values in properties.items():
                                headers.append(f"{cf}:{prop}")
                                latest_timestamp = max(values.keys())
                                row.append(values[latest_timestamp])
                        
                        table.field_names = headers
                        table.add_row(row)
                        
                        print(table)
                        break
        
        if not foundTable:
            console.print(f'ERROR: Tabla {tableName} no encontrada.', style=red)
        elif not foundRow:
            console.print(f'ERROR: Fila con ID {rowID} no encontrada en la tabla {tableName}.', style=red)


    """
    Función para escanear una tabla en HBase
    * tableName: Nombre de la tabla a escanear
    """
    def scan(self, tableName):
        foundTable = False
        
        for file in os.listdir(self.directory):
            if file.endswith('.json'):
                filePath = os.path.join(self.directory, file)
                with open(filePath, 'r') as f:
                    data = json.load(f)
                
                if data["metadata"]["table_name"] == tableName:
                    foundTable = True
                    allRows = data["rows_data"]

                    groupedRows = {}

                    for rowID, rowData in allRows.items():
                        #Obtener las propiedades de cada column family para agrupar las filas
                        propertiesSignature = {}
                        for cf, properties in rowData.items():
                            propertiesSignature[cf] = tuple(sorted(properties.keys()))
                        
                        #Convertir el diccionario a una tupla para usarlo como clave
                        propertiesSignature = tuple(sorted(propertiesSignature.items()))

                        if propertiesSignature not in groupedRows:
                            groupedRows[propertiesSignature] = []
                        
                        groupedRows[propertiesSignature].append((rowID, rowData))
                    
                    #Imprimir los grupos de filas
                    for propertiesSignature, rows in groupedRows.items():
                        #Crear tabla para las filas
                        rowTable = PrettyTable()
                        if rows:
                            headers = ["Row key"]
                            for cf, properties in rows[0][1].items():
                                for prop in properties.keys():
                                    headers.append(f"{cf}:{prop}")
                            rowTable.field_names = headers

                            for rowID, rowData in rows:
                                row = [rowID]
                                for cf, properties in rowData.items():
                                    for prop, values in properties.items():
                                        latest_timestamp = max(values.keys())
                                        cell_value = f"{latest_timestamp}\n{values[latest_timestamp]}"
                                        row.append(cell_value)
                                rowTable.add_row(row, divider=True)

                        print(rowTable)
                    break
        
        if not foundTable:
            console.print(f'ERROR: Tabla {tableName} no encontrada.', style=red)

    """
    Función para eliminar una celda, una fila o una familia de columnas en una tabla de HBase
    * tableName: Nombre de la tabla
    """
    def delete(self, tableName, action):        
        foundTable = False
        
        for file in os.listdir(self.directory):
            if file.endswith('.json'):
                filePath = os.path.join(self.directory, file)
                with open(filePath, 'r') as f:
                    data = json.load(f)
                
                if data["metadata"]["table_name"] == tableName:
                    data["metadata"]["modified"] = datetime.now().isoformat()
                    foundTable = True
                    
                    if action == 'c':
                        rowKey = input("Ingrese la row key: ").strip()
                        columnFamily = input("Ingrese la column family: ").strip()
                        qualifier = input("Ingrese el qualifier: ").strip()
                        
                        if rowKey in data["rows_data"]:
                            if columnFamily in data["rows_data"][rowKey]:
                                if qualifier in data["rows_data"][rowKey][columnFamily]:
                                    del data["rows_data"][rowKey][columnFamily][qualifier]
                                    if not data["rows_data"][rowKey][columnFamily]:
                                        del data["rows_data"][rowKey][columnFamily]
                                    console.print(f'SISTEMA: Celda eliminada {rowKey} - {columnFamily}:{qualifier}', style=blue)
                                else:
                                    console.print(f'ERROR: No se encontró el qualifier {qualifier} en la column family {columnFamily}.', style=red)
                            else:
                                console.print(f'ERROR: No se encontró la column family {columnFamily} en la fila {rowKey}.', style=red)
                        else:
                            console.print(f'ERROR: No se encontró la fila con row key {rowKey}.', style=red)
                    
                    elif action == 'r':
                        rowKey = input("Ingrese la row key: ").strip()
                        
                        if rowKey in data["rows_data"]:
                            del data["rows_data"][rowKey]
                            console.print(f'SISTEMA: Fila eliminada {rowKey}', style=blue)
                        else:
                            console.print(f'ERROR: No se encontró la fila con row key {rowKey}.', style=red)
                    
                    elif action == 'f':
                        rowKey = input("Ingrese la row key: ").strip()
                        columnFamily = input("Ingrese la column family: ").strip()
                        
                        if rowKey in data["rows_data"]:
                            if columnFamily in data["rows_data"][rowKey]:
                                del data["rows_data"][rowKey][columnFamily]
                                console.print(f'SISTEMA: Column family eliminada {rowKey} - {columnFamily}', style=blue)
                            else:
                                console.print(f'ERROR: No se encontró la column family {columnFamily} en la fila {rowKey}.', style=red)
                        else:
                            console.print(f'ERROR: No se encontró la fila con row key {rowKey}.', style=red)
                    
                    else:
                        print("Acción no válida. Use 'c' para eliminar una celda, 'r' para eliminar una fila o 'f' para eliminar una familia de columnas.")
                    
                    #Guardar los cambios en el archivo JSON
                    with open(filePath, 'w') as f_write:
                        json.dump(data, f_write, indent=4)
                    break
        
        if not foundTable:
            console.print(f'ERROR: Tabla {tableName} no encontrada.', style=red)

    """
    Función para eliminar una fila en una tabla de HBase
    * tableName: Nombre de la tabla
    * rowKey: ID de la fila a eliminar
    """
    def delete_all(self, tableName, rowKey):
        foundTable = False
        
        for file in os.listdir(self.directory):
            if file.endswith('.json'):
                filePath = os.path.join(self.directory, file)
                with open(filePath, 'r') as f:
                    data = json.load(f)
                
                if data["metadata"]["table_name"] == tableName:
                    data["metadata"]["modified"] = datetime.now().isoformat()
                    foundTable = True
                    
                    if rowKey in data["rows_data"]:
                        del data["rows_data"][rowKey]
                        console.print(f'SISTEMA: Fila eliminada {rowKey}', style=blue)
                        
                        #Guardar los cambios en el archivo JSON
                        with open(filePath, 'w') as f_write:
                            json.dump(data, f_write, indent=4)
                    else:
                        console.print(f'ERROR: No se encontró la fila con row key {rowKey}.', style=red)
                    break
        
        if not foundTable:
            console.print(f'ERROR: Tabla {tableName} no encontrada.', style=red)

    """
    Función para contar las filas de una tabla en HBase
    * tableName: Nombre de la tabla
    """
    def count(self, tableName):
        foundTable = False
        
        for file in os.listdir(self.directory):
            if file.endswith('.json'):
                filePath = os.path.join(self.directory, file)
                with open(filePath, 'r') as f:
                    data = json.load(f)
                
                if data["metadata"]["table_name"] == tableName:
                    foundTable = True
                    row_count = len(data["rows_data"])
                    console.print(f'Cantidad de filas en la tabla {tableName}: {row_count}', style=green)
                    break
        
        if not foundTable:
            console.print(f'ERROR: Tabla {tableName} no encontrada.', style=red)

    """
    Función para truncar las filas de una tabla en HBase
    * tableName: Nombre de la tabla
    """
    def truncate(self, tableName):
        foundTable = False
        
        for file in os.listdir(self.directory):
            if file.endswith('.json'):
                filePath = os.path.join(self.directory, file)
                with open(filePath, 'r') as f:
                    data = json.load(f)
                
                if data["metadata"]["table_name"] == tableName:
                    data["metadata"]["modified"] = datetime.now().isoformat()
                    foundTable = True
                    data["metadata"]["disabled"] = True
                    console.print(f'SISTEMA: Tabla {tableName} ha sido deshabilitada.\n', style=blue)
                    
                    console.print('Eliminando todas las filas...', style=green)
                    barColor = "\033[32m"
                    for _ in tqdm(range(100), desc="Progreso", ncols=100, bar_format=f"{barColor}{{bar}}\033[00m"):
                        time.sleep(0.03)  # Simulación de carga
                    
                    data["rows_data"] = {}
                    data["metadata"]["rows_counter"] = 0
                    
                    with open(filePath, 'w') as f_write:
                        json.dump(data, f_write, indent=4)
                    
                    console.print(f'\nSISTEMA: Todas las filas de la tabla {tableName} han sido eliminadas.', style=blue)
                    break
        
        if not foundTable:
            console.print(f'ERROR: Tabla {tableName} no encontrada.', style=red)


"""
Función para imprime los comandos disponibles
"""
def printComands():
    table = PrettyTable()
    table.field_names = ["Comando", "Funcionalidad"]
    table.add_row(["create", "Crear nueva tabla"])
    table.add_row(["list", "Listar tablas de la base de datos"])
    table.add_row(["disable", "Deshabilitar una tabla"])
    table.add_row(["enable", "Habilitar una tabla"])
    table.add_row(["is_enabled", "Verficar estado de una tabla"])
    table.add_row(["alter", "Alterar elementos de una tabla"])
    table.add_row(["drop", "Eliminar una tabla"])
    table.add_row(["drop_all", "Eliminar tablas que conicidan con un patrón"])
    table.add_row(["describe", "Describir una tabla"])
    table.add_row(["put", "Insertar/Actualizar fila"])
    table.add_row(["get", "Obtener datos de una fila"])
    table.add_row(["scan", "Escanear una tabla"])
    table.add_row(["delete", "Eliminar una celda, fila o column family de una tabla"])
    table.add_row(["delete_all", "Eliminar una fila de una tabla"])
    table.add_row(["count", "Contar filas de una tabla"])
    table.add_row(["truncate", "Truncar filas de una tabla"])
    table.add_row(["help", "Imprimir los comandos disponibles"])
    table.add_row(["exit", "Salir del programa"])

    print(table)

#Ejecución del programa
if __name__ == '__main__':
    hbase = HBase()

    #Imprimir bienvenida
    asciiHBase = pyfiglet.figlet_format("HBase Simulator")
    print(asciiHBase)
    console.print("A continuación escriba el comando que desea ejecutar:", style=magenta)
    printComands()
    print()
    
    while True:
        command = input('> ').strip().lower()
        
        if command == 'create':
            try:
                tableName = input("Ingrese el nombre de la tabla: ").strip()
                columnFamilies = input("Ingrese las column families separadas por comas: ").strip().split(',')
                columnFamilies = [cf.strip() for cf in columnFamilies]
                versions = int(input("Ingrese el número máximo de versiones de celda que se almacenarán: ").strip())
                fileName = tableName + ".json"
                hbase.create(fileName, tableName, columnFamilies, versions)
            
            except Exception as e:
                print()
                console.print(f"ERROR: No fue posible crear la tabla: {e}", style=red)
        
        elif command == 'list':
            try:
                tablesList = hbase.list()
            except Exception as e:
                print()
                console.print(f"ERROR: No fue posible listar las tabla: {e}", style=red)

        elif command == 'disable':
            try:
                tableName = input("Ingrese el nombre de la tabla: ").strip()
                hbase.changeStatus(tableName, "disable")
            
            except Exception as e:
                print()
                console.print(f"ERROR: No fue posible deshabilitar la tabla: {e}", style=red)

        elif command == 'enable':
            try:
                tableName = input("Ingrese el nombre de la tabla: ").strip()
                hbase.changeStatus(tableName, "enable")
            
            except Exception as e:
                print()
                console.print(f"ERROR: No fue posible habilitar la tabla: {e}", style=red)

        elif command == 'is_enabled':
            try:
                tableName = input("Ingrese el nombre de la tabla: ").strip()
                hbase.is_enabled(tableName)
            
            except Exception as e:
                print()
                console.print(f"ERROR: No fue posible verificar el estado de la tabla: {e}", style=red)
            
        elif command == 'alter':
            try:
                oldTableName = input("Ingrese el nombre de la tabla a editar: ").strip()
                newTableName = input("Ingrese el nuevo nombre de la tabla: ").strip()
                newColumnFamilies = input("Ingrese las column families a agregar separadas por comas (presione ENTER para omitir): ").strip().split(',')
                newColumnFamilies = [cf.strip() for cf in newColumnFamilies]
                
                hbase.alter(oldTableName, newTableName, newColumnFamilies)
            
            except Exception as e:
                print()
                console.print(f"ERROR: No fue posible alterar la tabla: {e}", style=red)
        
        elif command == 'drop':
            try:
                tableName = input("Ingrese el nombre de la tabla a eliminar: ").strip()
                hbase.drop(tableName)
            
            except Exception as e:
                print()
                console.print(f"ERROR: No fue posible eliminar la tabla: {e}", style=red)

        elif command == 'drop_all':
            try:
                pattern = input("Ingrese el patrón de las tablas a eliminar: ").strip()
                hbase.drop_all(pattern)
            
            except Exception as e:
                print()
                console.print(f"ERROR: No fue posible eliminar las tablas: {e}", style=red)
        
        elif command == 'describe':
            try:
                tableName = input("Ingrese el nombre de la tabla a describir: ").strip()
                hbase.describe(tableName)
            
            except Exception as e:
                print()
                console.print(f"ERROR: No fue posible describir la tabla: {e}", style=red)
        
        elif command == 'put':
            try:
                tableName = input("Ingrese el nombre de la tabla: ").strip()
                action = input("¿Desea insertar (i) o actualizar (u) una fila? ").strip().lower()
                hbase.put(tableName, action)
            
            except Exception as e:
                print()
                console.print(f"ERROR: No fue posible insertar o actualizar la fila: {e}", style=red)

        elif command == 'get':
            try:
                tableName = input("Ingrese el nombre de la tabla: ").strip()
                rowID = input("Ingrese el ID de la fila: ").strip()
                hbase.get(tableName, rowID)
            
            except Exception as e:
                print()
                console.print(f"ERROR: No fue posible obtener la fila: {e}", style=red)

        elif command == 'scan':
            try:
                tableName = input("Ingrese el nombre de la tabla: ").strip()
                hbase.scan(tableName)
            
            except Exception as e:
                print()
                console.print(f"ERROR: No fue posible escanear la tabla: {e}", style=red)

        elif command == 'delete':
            try:
                tableName = input("Ingrese el nombre de la tabla: ").strip()
                action = input("¿Desea eliminar una celda (c), una fila (r) o una familia de columnas (f)? ").strip().lower()
                hbase.delete(tableName, action)
            
            except Exception as e:
                print()
                console.print(f"ERROR: No fue posible ejecutar la función delete: {e}", style=red)

        elif command == 'delete_all':
            try:
                tableName = input("Ingrese el nombre de la tabla: ").strip()
                rowKey = input("Ingrese la row key: ").strip()
                hbase.delete_all(tableName, rowKey)
            
            except Exception as e:
                print()
                console.print(f"ERROR: No fue posible eliminar la fila: {e}", style=red)

        elif command == 'count':
            try:
                tableName = input("Ingrese el nombre de la tabla: ").strip()
                hbase.count(tableName)
            
            except Exception as e:
                print()
                console.print(f"ERROR: No fue posible contar la filas de la tabla: {e}", style=red)
        
        elif command == 'truncate':
            try:
                tableName = input("Ingrese el nombre de la tabla: ").strip()
                hbase.truncate(tableName)
            
            except Exception as e:
                print()
                console.print(f"ERROR: No fue posible truncar la tabla: {e}", style=red)

        elif command == 'help':
            printComands()
        
        elif command == 'exit':
            console.print("\n¡Gracias por utilizar el programa!", style=magenta)
            break
        
        else:
            console.print("ERROR: Comando desconocido.", style=red)
