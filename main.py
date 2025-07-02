import os
import csv
import time
import tracemalloc
import multiprocessing
from bnb import bnb_knapsack

def read_items_from_csv(filename):
    items = []
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"Arquivo CSV '{filename}' está vazio ou sem cabeçalho.")
        fieldnames = {name.strip().lower(): name for name in reader.fieldnames}
        for row in reader:
            price = int(row[fieldnames["price"]])
            weight = int(row[fieldnames["weight"]])
            items.append((weight, price))
    return items

def read_optimal_metadata(csv_path):
    data = {}
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) == 2:
                key, value = row
                data[key] = value
    n = int(data["n"])
    W = int(data["c"])
    valor_otimo = int(data["z"])
    return n, W, valor_otimo

def run_bnb_with_timeout(items, W, queue):
    tracemalloc.start()
    start = time.time()
    valor_alg, total_nodes, max_queue_len = bnb_knapsack(items, W)
    duracao = time.time() - start
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    queue.put((valor_alg, total_nodes, max_queue_len, duracao, current, peak))

# Pastas
csv_items_folder = "ls-csv"
optimal_folder = "ls-optimal"
saida_csv = "resultados-ls.csv"
TIMEOUT = 1800  # 30 minutos

# Cria CSV e escreve cabeçalho
with open(saida_csv, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([
        "arquivo", "n_itens", "W", "valor_otimo",
        "valor_algoritmo", "n_nos", "n_fila", "tempo_seg",
        "memoria_kb", "memoria_pico_kb", "status"
    ])

for fname in sorted(os.listdir(csv_items_folder)):
    item_csv_path = os.path.join(csv_items_folder, fname)
    optimal_csv_path = os.path.join(optimal_folder, fname)

    if not os.path.isfile(item_csv_path) or not os.path.isfile(optimal_csv_path):
        continue

    try:
        items = read_items_from_csv(item_csv_path)
        n, W, valor_otimo = read_optimal_metadata(optimal_csv_path)
    except Exception as e:
        print(f"Erro ao processar {fname}: {e}")
        continue

    print(f"Rodando {fname} - n: {n}, W: {W}")

    queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=run_bnb_with_timeout, args=(items, W, queue))
    process.start()
    process.join(timeout=TIMEOUT)

    if process.is_alive():
        process.terminate()
        process.join()
        resultado = [fname, n, W, valor_otimo, "-", "-", "-", "-", "-", "-", "TIMEOUT"]
    else:
        try:
            valor_alg, total_nodes, max_queue_len, duracao, current, peak = queue.get_nowait()
            status = "OK" if valor_alg == valor_otimo else "ERRO"
            resultado = [
                fname, n, W, valor_otimo, valor_alg, total_nodes, max_queue_len,
                round(duracao, 6), round(current / 1024, 2), round(peak / 1024, 2), status
            ]
        except:
            resultado = [fname, n, W, valor_otimo, "-", "-", "-", "-", "-", "-", "FALHA"]

    # Salva o resultado incrementalmente
    with open(saida_csv, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(resultado)

print(f"Resultados salvos em {saida_csv}")