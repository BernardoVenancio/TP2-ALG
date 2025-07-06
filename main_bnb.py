import os
import csv
import tracemalloc
from utils import read_items_from_csv, read_optimal_metadata, get_file_pairs
from bnb import bnb_knapsack

TIMEOUT = 1800

configuracoes = [
    {"nome": "low", "input_path": "instancias/low/inputs", "opt_path": "instancias/low/labels", "saida_csv": "resultados/bnb/low.csv"},
    {"nome": "large", "input_path": "instancias/large/inputs", "opt_path": "instancias/large/labels", "saida_csv": "resultados/bnb/large.csv"}
]

for config in configuracoes:
    print(f"\nProcessando instâncias: {config['nome']}")
    saida_csv = config["saida_csv"]

    # Carrega nomes já processados
    arquivos_processados = set()
    if os.path.exists(saida_csv):
        with open(saida_csv, 'r') as f:
            reader = csv.reader(f)
            next(reader, None)  # pula cabeçalho
            for row in reader:
                if row and row[0]:
                    arquivos_processados.add(row[0])

    # Abre o CSV em modo append
    novo_arquivo = not os.path.exists(saida_csv)
    with open(saida_csv, 'a', newline='') as f:
        writer = csv.writer(f)
        if novo_arquivo:
            writer.writerow([
                "arquivo", "n_itens", "W", "valor_otimo", "valor_algoritmo",
                "n_nos", "n_fila", "tempo_seg", "memoria_kb", "memoria_pico_kb", "status"
            ])

        for fname, item_csv_path, optimal_csv_path in get_file_pairs(config["input_path"], config["opt_path"]):
            if fname in arquivos_processados:
                print(f"Pulando {fname} (já processado)")
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

                status = "TIMEOUT" if result.timeout else ("OK" if result.best_value == valor_otimo else "ERRO")
                row = [fname, n, W, valor_otimo, result.best_value, result.total_nodes,
                       result.max_queue_size, round(result.duration, 6),
                       round(current / 1024, 2), round(peak / 1024, 2), status]
            except Exception as e:
                tracemalloc.stop()
                print(f"Falha durante execução de {fname}: {e}")
                row = [fname, n, W, valor_otimo, "-", "-", "-", "-", "-", "-", "FALHA"]

            writer.writerow(row)
            f.flush()

    print(f"Resultados salvos em {saida_csv}")
