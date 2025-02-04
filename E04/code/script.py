import pandas as pd
import matplotlib.pyplot as plt
import logging
import os

# Configuració del logging
logging.basicConfig(filename='../../E02/fitxer_log.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Fitxer CSV
def exportar_resums_csv(annual_stats, fitxer_csv):
    try:
        file_path = os.path.join("../../E03", fitxer_csv)

        annual_stats.to_csv(file_path, index=True)
        logging.info(f"Resum estadístic exportat a {fitxer_csv}")
    except Exception as e:
        logging.error(f"Error exportant resum a CSV: {e}")
        raise

# Gràfics
def grafics(annual_stats):
    try:
        plt.figure(figsize=(10, 6))
        annual_stats['total_precip'].plot(kind='bar', color='skyblue')
        plt.title('Precipitació Total por Año')
        plt.xlabel('Any')
        plt.ylabel('Precipitació Total')
        plt.tight_layout()
        plt.savefig(os.path.join("../../E03", 'grafic_total_precip.png'))
        plt.close()

        plt.figure(figsize=(10, 6))
        annual_stats['Annual_Variation'].plot(kind='line', marker='o', color='orange')
        plt.title('Tasa de Canvi Anual (%)')
        plt.xlabel('Any')
        plt.ylabel('Canvi (%)')
        plt.grid()
        plt.tight_layout()
        plt.savefig(os.path.join("../../E03", 'grafic_variacio_anual.png'))
        plt.close()

    except Exception as e:
        logging.error(f"Error generant gràfics: {e}")
        raise

# Lectura de archivos
def lectura_arxiu(ruta):
    try:
        with open(ruta, 'r') as file:
            lines = file.readlines()

        # Separar datos
        data = []
        for line in lines[2:]:
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

# Estadísticas anuales
def calculate_annual_statistics(df):
    df['Total_Precip'] = df.iloc[:, 3:].sum(axis=1)  # Sumar las precipitaciones de cada fila (cada día)
    df['Average_Precip'] = df.iloc[:, 3:].mean(axis=1)  # Promedio de precipitaciones por año

    annual_stats = df.groupby('Year').agg(
        total_precip=('Total_Precip', 'sum'),
        avg_precip=('Average_Precip', 'mean'),
        min_precip=('Total_Precip', 'min'),
        max_precip=('Total_Precip', 'max'),
        std_precip=('Total_Precip', 'std'),
        avg_month_precip=('Average_Precip', 'mean')
    )

    # Asegurarse de que las columnas de precipitación sean de tipo float antes de calcular el cambio porcentual
    annual_stats['total_precip'] = annual_stats['total_precip'].astype(float)
    annual_stats['Annual_Variation'] = annual_stats['total_precip'].pct_change() * 100  # Tasa de cambio anual en porcentaje
    return annual_stats

# Mostrar el informe general
def mostrar_informe(global_stats, num_archivos, annual_stats):
    missing_percentage = (global_stats['missing_values'] / global_stats['total_values']) * 100

    print("=============================================================")
    print("ANÁLISIS DE PRECIPITACIÓN - INFORME COMPLETO")
    print("=============================================================")
    print("\n1. ESTADÍSTICAS GENERALES")
    print("-------------------------------------------------------------")
    print(f"Total de valores procesados: {global_stats['total_values']:,}")
    print(f"Valores faltantes (-999): {global_stats['missing_values']:,}")
    print(f"Porcentaje de datos faltantes: {missing_percentage:.2f}%")
    print(f"Archivos procesados: {num_archivos:,}")
    print(f"Líneas procesadas: {global_stats['total_lines']:,}")
    print("=============================================================")

    print("\n2. ESTADÍSTICAS ANUALES")
    print("-------------------------------------------------------------")

    # Precipitació total y mitjana por any
    print("\nPrecipitació total y mitjana por any (primer 5 anys):")
    print(annual_stats[['total_precip', 'avg_precip']].head(), "\n")

    # Tasa de canvi anual de les precipitacions
    print("Tasa de canvi anual de les precipitacions (%):")
    print(annual_stats[['Annual_Variation']].dropna().round(2).head(), "\n")

    # Variació estàndar anual de les precipitacions
    print("Variació estàndar anual de les precipitacions:")
    print(annual_stats[['std_precip']].dropna().round(2).head(), "\n")

    # Mitjana mensual de precipitacions
    avg_month_precip = annual_stats['avg_month_precip'].mean()
    print(f"Mitjana mensual de precipitacions: {avg_month_precip:.2f} mm\n")

    # Anys més plujosos y més secs
    print("Anys más pluviosos y más secos:")
    max_precip_year = annual_stats['max_precip'].idxmax()
    min_precip_year = annual_stats['min_precip'].idxmin()
    print(f"Anys més plujós: {max_precip_year} amb {annual_stats['max_precip'].max():,.2f} mm")
    print(f"Any més sec: {min_precip_year} amb {annual_stats['min_precip'].min():,.2f} mm\n")
    print("=============================================================\n")

# Variables
ruta_carpeta = '../../E01/dades'
prefix = 'precip'

# Inicializar estadísticas globales
global_stats = {
    'total_values': 0,
    'missing_values': 0,
    'total_lines': 0
}
num_archivos = 0

# Bucle
annual_stats_list = []
files_found = False

for arxiu in sorted(os.listdir(ruta_carpeta), key=lambda x: int(''.join(filter(str.isdigit, x))) if x.startswith(prefix) else float('inf')):
    if arxiu.startswith(prefix):
        files_found = True

        ruta = os.path.join(ruta_carpeta, arxiu)

        # Procesar el archivo
        try:
            dataframe = lectura_arxiu(ruta)
            global_stats = calculate_global_statistics(dataframe, global_stats)
            num_archivos += 1

            # Calcular estadísticas anuales
            annual_stats = calculate_annual_statistics(dataframe)
            annual_stats_list.append(annual_stats)

            print(f"Procesando {arxiu}: ÉXITO")
        except Exception as e:
            logging.error(f"Procesando {arxiu}: ERROR: {e}")

# Concatenar estadísticas anuales
if annual_stats_list:
    annual_stats_all = pd.concat(annual_stats_list)

    # Mostrar informe general
    mostrar_informe(global_stats, num_archivos, annual_stats_all)

    # Exportar resumen a CSV
    exportar_resums_csv(annual_stats_all, "resum_estadistic.csv")

    # Mostrar gráficos
    grafics(annual_stats_all)