import os
import csv

instance_folder = "large_scale"
saida_folder = "ls-cv"

os.makedirs(saida_folder, exist_ok=True)

for fname in sorted(os.listdir(instance_folder)):
    instance_path = os.path.join(instance_folder, fname)

    if not os.path.isfile(instance_path):
        continue

    csv_name = os.path.splitext(fname)[0] + ".csv"
    csv_path = os.path.join(saida_folder, csv_name)

    with open(instance_path, 'r') as f:
        lines = f.readlines()[1:]  # Ignora a primeira linha

    dados = []
    for line in lines:
        parts = line.strip().split()
        if len(parts) != 2:
            continue  # ignora linhas inválidas
        valor, peso = map(int, parts)
        dados.append((valor, peso))

    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["price", "weight"])
        writer.writerows(dados)

    print(f"Arquivo salvo: {csv_path}")

# Pastas
instance_folder = "large_scale"
optimum_folder = "large_scale-optimum"
saida_folder = "ls-optimal"

os.makedirs(saida_folder, exist_ok=True)

for fname in sorted(os.listdir(instance_folder)):
    instance_path = os.path.join(instance_folder, fname)
    optimum_path = os.path.join(optimum_folder, fname)

    if not os.path.isfile(instance_path) or not os.path.isfile(optimum_path):
        continue

    # Lê n e c da primeira linha
    with open(instance_path, 'r') as f:
        linha = f.readline()
        n, c = map(int, linha.strip().split())

    # Lê z (valor ótimo)
    with open(optimum_path, 'r') as f:
        z = int(f.readline().strip())

    # Tempo inicial
    tempo = 0.00

    # Caminho do CSV de saída
    csv_name = os.path.splitext(fname)[0] + ".csv"
    csv_path = os.path.join(saida_folder, csv_name)

    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["n", n])
        writer.writerow(["c", c])
        writer.writerow(["z", z])
        writer.writerow(["time", f"{tempo:.2f}"])

    print(f"Arquivo salvo em formato chave-valor: {csv_path}")
