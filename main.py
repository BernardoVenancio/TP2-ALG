import os
import csv
import tracemalloc
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

TIMEOUT = 1800  # 30 minutos

# Define configurações para cada tipo
configuracoes = [
    {
        "nome": "low",
        "input_path": "instancias/low/inputs",
        "opt_path": "instancias/low/labels",
        "saida_csv": "resultados/low-result.csv"
    },
    {
        "nome": "large",
        "input_path": "instancias/large/inputs",
        "opt_path": "instancias/large/labels",
        "saida_csv": "resultados/large-result.csv"
    }
]

for config in configuracoes:
    print(f"\nProcessando instâncias: {config['nome']}")

    # Cria CSV e escreve cabeçalho
    with open(config["saida_csv"], 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            "arquivo", "n_itens", "W", "valor_otimo",
            "valor_algoritmo", "n_nos", "n_fila", "tempo_seg",
            "memoria_kb", "memoria_pico_kb", "status"
        ])

    for fname in sorted(os.listdir(config["input_path"])):
        item_csv_path = os.path.join(config["input_path"], fname)
        optimal_csv_path = os.path.join(config["opt_path"], fname)

        if not os.path.isfile(item_csv_path) or not os.path.isfile(optimal_csv_path):
            continue

        try:
            items = read_items_from_csv(item_csv_path)
            n, W, valor_otimo = read_optimal_metadata(optimal_csv_path)
        except Exception as e:
            print(f"Erro ao processar {fname}: {e}")
            continue

        print(f"Rodando {fname} - n: {n}, W: {W}")

        tracemalloc.start()
        try:
            result = bnb_knapsack(items, W, timeout_seconds=TIMEOUT)
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            if result.timeout_ocorreu:
                status = "TIMEOUT"
            else:
                status = "OK" if result.best_value == valor_otimo else "ERRO"

            resultado = [
                fname, n, W, valor_otimo, result.best_value, result.total_nodes,
                result.max_queue_size, round(result.duration, 6),
                round(current / 1024, 2), round(peak / 1024, 2), status
            ]
        except Exception as e:
            tracemalloc.stop()
            print(f"Falha durante execução de {fname}: {e}")
            resultado = [fname, n, W, valor_otimo, "-", "-", "-", "-", "-", "-", "FALHA"]

        with open(config["saida_csv"], 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(resultado)

    print(f"Resultados salvos em {config['saida_csv']}")
