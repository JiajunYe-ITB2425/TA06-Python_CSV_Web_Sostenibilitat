import pandas as pd
import logging
import os

# Configuració del logging
logging.basicConfig(filename='process_log.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def lectura_arxiu(ruta):
    try:
        # Llegir el fitxer línia per línia per evitar errors de delimitadors
        with open(ruta, 'r') as file:
            lines = file.readlines()

        # Separar capçalera, metadades i dades
        header = lines[0].strip()
        metadata = lines[1].strip()
        data_lines = lines[2:]

        # Processar les dades principals
        data = []
        for line in data_lines:
            fields = line.strip().split()
            data.append(fields)

        # Convertir les dades en DataFrame
        columns = ['Region', 'Year', 'Month'] + [f'Day_{i + 1}' for i in range(31)]
        df = pd.DataFrame(data, columns=columns[:len(data[0])])

        # Convertir columnes numèriques i gestionar valors mancants (-999)
        numeric_columns = df.columns[3:]
        df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')
        df.replace(-999, pd.NA, inplace=True)

        logging.info(f"Fitxer carregat i validat amb èxit: {ruta}")
        return df

    except Exception as e:
        logging.error(f"Error processant el fitxer {ruta}: {e}")
        raise

def calculate_statistics(df):
    try:
        # Percentatge de valors mancants
        missing_percentage = df.isna().mean() * 100

        # Estadístiques bàsiques
        annual_totals = df.groupby('Year').sum(numeric_only=True).sum(axis=1)
        annual_means = df.groupby('Year').mean(numeric_only=True).mean(axis=1)

        # Tendència anual
        trend = annual_totals.pct_change() * 100

        # Extrems
        max_year = annual_totals.idxmax()
        min_year = annual_totals.idxmin()

        # Resultats
        results = {
            'missing_percentage': missing_percentage,
            'annual_totals': annual_totals,
            'annual_means': annual_means,
            'trend': trend,
            'max_year': max_year,
            'min_year': min_year
        }
        return results

    except Exception as e:
        logging.error(f"Error calculant estadístiques: {e}")
        raise

# Variables
ruta_carpeta = 'E04/dades/'
prefix = 'precip'

# Bucle
for arxiu in sorted(os.listdir(ruta_carpeta), key=lambda x: int(''.join(filter(str.isdigit, x))) if x.startswith(prefix) else float('inf')):
    if arxiu.startswith(prefix):
        ruta = os.path.join(ruta_carpeta, arxiu)
        logging.info(f"Processant el fitxer: {arxiu}")

        # Processar el fitxer
        try:
            dataframe = lectura_arxiu(ruta)
            stats = calculate_statistics(dataframe)

            # Mostrar resultats
            print(f"Processant {arxiu}: ÈXIT")
        except Exception as e:
            logging.error(f"Processant {arxiu}: ERROR: {e}")