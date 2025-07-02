import os
import csv
import time
import tracemalloc
from bnb import bnb_knapsack

def read_items_from_csv(filename):
    items = []
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)

        if reader.fieldnames is None:
            raise ValueError(f"Arquivo CSV '{filename}' está vazio ou sem cabeçalho.")

        # Normaliza os nomes das colunas
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

# Pastas
csv_items_folder = "large-csv"
optimal_folder = "large-optimal"
saida_csv = "resultados-large.csv"

resultados = []

for fname in sorted(os.listdir(csv_items_folder)):
    item_csv_path = os.path.join(csv_items_folder, fname)
    optimal_csv_path = os.path.join(optimal_folder, fname)

    if not os.path.isfile(item_csv_path) or not os.path.isfile(optimal_csv_path):
        continue

    # Lê os itens do CSV
    items = read_items_from_csv(item_csv_path)

    # Lê metadados otimizados
    n, W, valor_otimo = read_optimal_metadata(optimal_csv_path)

    print(f"Rodando {fname} - n: {n}, W: {W}")

    # Medição de tempo e memória
    tracemalloc.start()
    start = time.time()
    valor_alg, total_nodes, max_queue_len = bnb_knapsack(items, W)
    duracao = time.time() - start
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    status = "OK" if valor_alg == valor_otimo else "ERRO"

    resultados.append([
        fname,
        n,
        W,
        valor_otimo,
        valor_alg,
        total_nodes,
        max_queue_len,
        round(duracao, 6),
        round(current / 1024, 2),
        round(peak / 1024, 2),
        status
    ])

# Salvar CSV com os resultados
with open(saida_csv, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([
        "arquivo", "n_itens", "W", "valor_otimo",
        "valor_algoritmo", "n_nos", "n_fila", "tempo_seg",
        "memoria_kb", "memoria_pico_kb", "status"
    ])
    writer.writerows(resultados)

print(f"Resultados salvos em {saida_csv}")
