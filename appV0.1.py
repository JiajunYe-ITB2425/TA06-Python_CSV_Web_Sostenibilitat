#Grup Didac, Alberto, Steven i Jie
import pandas as pd
import logging
import os
import time
from tqdm import tqdm
from colorama import Fore, Style, init
from multiprocessing import Pool

# Initialize colorama
init(autoreset=True)

# Configuració del logging
process_logger = logging.getLogger('process')
process_logger.setLevel(logging.INFO)
process_handler = logging.FileHandler('process.log')
process_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
process_logger.addHandler(process_handler)

error_logger = logging.getLogger('error')
error_logger.setLevel(logging.ERROR)
error_handler = logging.FileHandler('errors.log')
error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
error_logger.addHandler(error_handler)

def lectura_arxiu(ruta):
    try:
        # Llegir el fitxer en chunks
        chunk_list = []
        for chunk in pd.read_csv(ruta, sep='\s+', header=None, skiprows=2, chunksize=1000):
            chunk_list.append(chunk)
        df = pd.concat(chunk_list, ignore_index=True)

        # Assignar noms de columnes
        columns = ['Region', 'Year', 'Month'] + [f'Day_{i + 1}' for i in range(31)]
        df.columns = columns

        # Verificar que cada mes té 31 valors de dia
        for index, row in df.iterrows():
            if len(row) != 34:  # 3 columnes inicials + 31 dies
                raise ValueError(f"El fitxer {ruta} té un error en la fila {index + 1}: no té 31 valors de dia.")
            # Verificar si hay letras en los datos
            if any(not str(value).replace('.', '', 1).isdigit() for value in row[3:]):
                raise ValueError(f"El fitxer {ruta} té lletres en la fila {index + 1}.")
            # Verificar si hay intervalos incorrectos (valores fuera de rango)
            if any(value < -999 or value > 999 for value in row[3:] if pd.notna(value)):
                raise ValueError(f"El fitxer {ruta} té valors fora de rang en la fila {index + 1}.")
            # Verificar si hay muchos espacios
            if any('  ' in str(value) for value in row):
                raise ValueError(f"El fitxer {ruta} té molts espais en la fila {index + 1}.")

        # Convertir columnes numèriques i gestionar valors mancants (-999)
        numeric_columns = df.columns[3:]
        df[numeric_columns] = pd.to_numeric(df[numeric_columns], errors='coerce')
        df.replace(-999, pd.NA, inplace=True)

        process_logger.info(f"Fitxer carregat i validat amb èxit: {ruta}")
        return df

    except Exception as e:
        error_logger.error(f"Error processant el fitxer {ruta}: {e}")
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
        error_logger.error(f"Error calculant estadístiques: {e}")
        raise

def process_file(arxiu):
    ruta = os.path.join(ruta_carpeta, arxiu)
    process_logger.info(f"Processant el fitxer: {arxiu}")

    try:
        dataframe = lectura_arxiu(ruta)
        stats = calculate_statistics(dataframe)
        process_logger.info(f"Estadístiques calculades per {arxiu}: {stats}")
    except Exception as e:
        error_logger.error(f"Processant {arxiu}: ERROR: {e}")

# Variables
ruta_carpeta = '../E01/proves/'
prefix = 'precip'

# Bucle
arxius = sorted(os.listdir(ruta_carpeta), key=lambda x: int(''.join(filter(str.isdigit, x))) if x.startswith(prefix) else float('inf'))
start_time = time.time()

try:
    with Pool() as pool:
        with tqdm(total=len(arxius), desc="Processant arxius", unit="fitxers", unit_scale=True, colour='green', ascii=False, ncols=100) as pbar:
            for _ in pool.imap_unordered(process_file, arxius):
                pbar.update(1)
                elapsed_time = time.time() - start_time
                remaining_time = (elapsed_time / pbar.n) * (pbar.total - pbar.n)
                pbar.set_postfix({
                    'Elapsed': f'{Fore.GREEN}{elapsed_time:.2f}s{Style.RESET_ALL}',
                    'Remaining': f'{Fore.YELLOW}{remaining_time:.2f}s{Style.RESET_ALL}',
                    'Speed': f'{Fore.CYAN}{pbar.n / elapsed_time:.2f} fitxers/s{Style.RESET_ALL}'
                })
except KeyboardInterrupt:
    print("\nProcess interrupted by user. Exiting...")
    process_logger.info("Process interrupted by user.")
