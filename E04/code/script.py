import pandas as pd
import logging
import os

# Configuración del logging
logging.basicConfig(filename='fitxer_log.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Lectura de archivos
def lectura_arxiu(ruta):
    try:
        with open(ruta, 'r') as file:
            lines = file.readlines()

        # Separar datos
        data = []
        for line in lines[2:]:  # Ignorar las dos primeras líneas (cabecera y metadatos)
            fields = line.strip().split()
            data.append(fields)

        # Crear DataFrame
        columns = ['Region', 'Year', 'Month'] + [f'Day_{i + 1}' for i in range(31)]
        df = pd.DataFrame(data, columns=columns[:len(data[0])])

        # Convertir a numérico y gestionar valores faltantes
        numeric_columns = df.columns[3:]
        df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')
        df.replace(-999, pd.NA, inplace=True)

        logging.info(f"Archivo procesado con éxito: {ruta}")
        return df

    except Exception as e:
        logging.error(f"Error procesando el archivo {ruta}: {e}")
        raise

# Estadísticas generales acumuladas
def calculate_global_statistics(df, global_stats):
    # Actualizar el total de valores
    global_stats['total_values'] += df.size

    # Actualizar los valores faltantes
    global_stats['missing_values'] += df.isna().sum().sum()

    # Contar líneas procesadas
    global_stats['total_lines'] += len(df)

    return global_stats

# Mostrar el informe general
def mostrar_informe(global_stats, num_archivos):
    missing_percentage = (global_stats['missing_values'] / global_stats['total_values']) * 100

    print("=============================================================")
    print("                ANÁLISIS DE PRECIPITACIÓN - INFORME COMPLETO")
    print("=============================================================")
    print("\n1. ESTADÍSTICAS GENERALES")
    print("-------------------------------------------------------------")
    print(f"Total de valores procesados: {global_stats['total_values']:,}")
    print(f"Valores faltantes (-999): {global_stats['missing_values']:,}")
    print(f"Porcentaje de datos faltantes: {missing_percentage:.2f}%")
    print(f"Archivos procesados: {num_archivos:,}")
    print(f"Líneas procesadas: {global_stats['total_lines']:,}")
    print("=============================================================\n")

# Variables
ruta_carpeta = '../../E01/proves'
prefix = 'precip'

# Inicializar estadísticas globales
global_stats = {
    'total_values': 0,
    'missing_values': 0,
    'total_lines': 0
}
num_archivos = 0

# Bucle
for arxiu in sorted(os.listdir(ruta_carpeta), key=lambda x: int(''.join(filter(str.isdigit, x))) if x.startswith(prefix) else float('inf')):
    if arxiu.startswith(prefix):
        ruta = os.path.join(ruta_carpeta, arxiu)

        # Procesar el archivo
        try:
            dataframe = lectura_arxiu(ruta)
            global_stats = calculate_global_statistics(dataframe, global_stats)
            num_archivos += 1

            print(f"Procesando {arxiu}: ÉXITO")
        except Exception as e:
            logging.error(f"Procesando {arxiu}: ERROR: {e}")

# Mostrar informe general
mostrar_informe(global_stats, num_archivos)
