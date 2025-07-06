import os
import csv

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
                data[key.strip().lower()] = value
    n = int(data["n"])
    W = int(data["c"])
    valor_otimo = int(data["z"])
    return n, W, valor_otimo

def get_file_pairs(input_dir, label_dir):
    for fname in sorted(os.listdir(input_dir)):
        input_path = os.path.join(input_dir, fname)
        label_path = os.path.join(label_dir, fname)
        if os.path.isfile(input_path) and os.path.isfile(label_path):
            yield fname, input_path, label_path
