import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import os

# Criar pasta de imagens
os.makedirs("imagens", exist_ok=True)

def carregar_capacidades(label_dirs):
    capacidades = {}
    for pasta in label_dirs:
        for nome_arquivo in os.listdir(pasta):
            if nome_arquivo.endswith(".txt"):
                caminho = os.path.join(pasta, nome_arquivo)
                with open(caminho, 'r') as f:
                    linhas = f.readlines()
                    for linha in linhas:
                        if linha.startswith("c,"):
                            capacidade = int(linha.strip().split(",")[1])
                            break
                nome_instancia = nome_arquivo.replace(".txt", "")
                capacidades[nome_instancia] = capacidade
    return capacidades

label_dirs = [
    "instancias/large/labels",
    "instancias/low/labels"
]

capacidades_dict = carregar_capacidades(label_dirs)

def adicionar_capacidade(df):
    df["instancia"] = df["arquivo"].str.replace(".csv", "", regex=False)
    df["capacidade_mochila"] = df["instancia"].map(capacidades_dict)
    return df

def load_datasets():
    datasets = {
        "branch_large": pd.read_csv("resultados/bnb/large_linear.csv"),
        "branch_low": pd.read_csv("resultados/bnb/low_linear.csv"),
        "fptas_large": pd.read_csv("resultados/fptas/large.csv"),
        "fptas_low": pd.read_csv("resultados/fptas/low.csv"),
        "greedy_large": pd.read_csv("resultados/greedy/large.csv"),
        "greedy_low": pd.read_csv("resultados/greedy/low.csv"),
    }
    return datasets

# Carregar e combinar datasets
data = load_datasets()
branch_df = pd.concat([data["branch_large"], data["branch_low"]], ignore_index=True)
fptas_df = pd.concat([data["fptas_large"], data["fptas_low"]], ignore_index=True)
greedy_df = pd.concat([data["greedy_large"], data["greedy_low"]], ignore_index=True)

todos_arquivos = set(branch_df["arquivo"]) | set(fptas_df["arquivo"]) | set(greedy_df["arquivo"])

# Mapear n_itens conhecidos a partir de todos os dataframes
n_itens_map = pd.concat([branch_df, fptas_df, greedy_df], ignore_index=True)[["arquivo", "n_itens"]].dropna().drop_duplicates().set_index("arquivo")["n_itens"].to_dict()

def preencher_faltantes(df, nome_algoritmo):
    arquivos_faltando = todos_arquivos - set(df["arquivo"])
    novos = []
    for arquivo in arquivos_faltando:
        novos.append({
            "arquivo": arquivo,
            "tempo_seg": 1800,
            "memoria_pico_kb": 0,
            "status": "TIMEOUT",
            "valor_algoritmo": np.nan,
            "valor_otimo": np.nan,
            "n_itens": n_itens_map.get(arquivo, np.nan)
        })
    df_completo = pd.concat([df, pd.DataFrame(novos)], ignore_index=True)
    return df_completo

branch_df = preencher_faltantes(branch_df, "Branch")
fptas_df = preencher_faltantes(fptas_df, "FPTAS")
greedy_df = preencher_faltantes(greedy_df, "Greedy")

# Marcar timeouts
branch_df["timeout"] = branch_df["status"] == "TIMEOUT"
fptas_df["timeout"] = fptas_df["status"] == "TIMEOUT"

# Adicionar capacidade da mochila
branch_df = adicionar_capacidade(branch_df)
fptas_df = adicionar_capacidade(fptas_df)
greedy_df = adicionar_capacidade(greedy_df)

# Filtrar instâncias sem timeout
ok_branch = branch_df[~branch_df["timeout"]]
ok_fptas = fptas_df[~fptas_df["timeout"]]
ok_greedy = greedy_df[greedy_df["tempo_seg"] < 1800]

# Gráfico Tempo vs N Itens
plt.figure(figsize=(10,7))
plt.scatter(ok_branch["n_itens"], ok_branch["tempo_seg"], label="Branch", color="blue", s=50, marker='o')
plt.scatter(ok_fptas["n_itens"], ok_fptas["tempo_seg"], label="FPTAS", color="green", s=50, marker='s')
plt.scatter(ok_greedy["n_itens"], ok_greedy["tempo_seg"], label="Greedy", color="purple", s=50, marker='^')
plt.xscale('log')
plt.yscale('log')
plt.xlabel("Número de Itens (escala log)", fontsize=12)
plt.ylabel("Tempo de Execução (s, escala log)", fontsize=12)
plt.title("Tempo de Execução por Número de Itens", fontsize=14, pad=15)
plt.legend(fontsize=10)
plt.grid(True, which="both", ls=":")
plt.tight_layout()
plt.savefig("imagens/tempo_vs_n_itens_comparativo.png")
plt.close()

# Gráfico Memória vs N Itens
plt.figure(figsize=(10,7))
plt.scatter(ok_branch["n_itens"], ok_branch["memoria_pico_kb"], label="Branch", color="blue", s=50, marker='o')
plt.scatter(ok_fptas["n_itens"], ok_fptas["memoria_pico_kb"], label="FPTAS", color="green", s=50, marker='s')
plt.scatter(ok_greedy["n_itens"], ok_greedy["memoria_pico_kb"], label="Greedy", color="purple", s=50, marker='^')
plt.xscale('log')
plt.yscale('log')
plt.xlabel("Número de Itens (escala log)", fontsize=12)
plt.ylabel("Memória Pico (KB, escala log)", fontsize=12)
plt.title("Memória Pico por Número de Itens", fontsize=14, pad=15)
plt.legend(fontsize=10)
plt.grid(True, which="both", ls=":")
plt.tight_layout()
plt.savefig("imagens/memoria_vs_n_itens_comparativo.png")
plt.close()

# Gráfico Erro Relativo
fptas_ok = ok_fptas.copy()
fptas_ok["erro_relativo_pct"] = 100 * (fptas_ok["valor_otimo"] - fptas_ok["valor_algoritmo"]) / fptas_ok["valor_otimo"]
greedy_ok = ok_greedy.copy()
greedy_ok["erro_relativo_pct"] = 100 * (greedy_ok["valor_otimo"] - greedy_ok["valor_algoritmo"]) / greedy_ok["valor_otimo"]

plt.figure(figsize=(10,7))
plt.scatter(fptas_ok["n_itens"], fptas_ok["erro_relativo_pct"], label="FPTAS", color="green", s=50, marker='s')
plt.scatter(greedy_ok["n_itens"], greedy_ok["erro_relativo_pct"], label="Greedy", color="purple", s=50, marker='^')
plt.xscale('log')
plt.xlabel("Número de Itens (escala log)", fontsize=12)
plt.ylabel("Erro relativo (%)", fontsize=12)
plt.title("Erro relativo em relação ao ótimo", fontsize=14, pad=15)
plt.legend(fontsize=10)
plt.grid(True, which="both", ls=":")
plt.tight_layout()
plt.savefig("imagens/erro_relativo_comparativo.png")
plt.close()

# Boxplot Tempo Execução
plt.figure(figsize=(10,6))
plt.boxplot([
    branch_df["tempo_seg"],
    fptas_df["tempo_seg"],
    greedy_df["tempo_seg"]
], tick_labels=["Branch", "FPTAS", "Greedy"], showmeans=True)
plt.yscale('log')
plt.ylabel("Tempo de Execução (s, escala log)", fontsize=12)
plt.title("Distribuição do Tempo de Execução (Boxplot)", fontsize=14, pad=15)
plt.grid(True, axis='y', ls=":")
plt.tight_layout()
plt.savefig("imagens/boxplot_tempo_comparativo.png")
plt.close()

# Histograma Memória Pico
plt.figure(figsize=(10,6))
max_memoria = max(branch_df["memoria_pico_kb"].max(), fptas_df["memoria_pico_kb"].max(), greedy_df["memoria_pico_kb"].max())
bins = np.logspace(np.log10(1), np.log10(max_memoria), 30)
plt.hist(branch_df["memoria_pico_kb"], bins=bins, color='blue', alpha=0.6, label="Branch")
plt.hist(fptas_df["memoria_pico_kb"], bins=bins, color='green', alpha=0.6, label="FPTAS")
plt.hist(greedy_df["memoria_pico_kb"], bins=bins, color='purple', alpha=0.6, label="Greedy")
plt.xscale('log')
plt.xlabel("Memória Pico (KB, escala log)", fontsize=12)
plt.ylabel("Número de Execuções", fontsize=12)
plt.title("Distribuição de Memória Pico (Histograma)", fontsize=14, pad=15)
plt.legend()
plt.grid(True, which="both", ls=":")
plt.tight_layout()
plt.savefig("imagens/histograma_memoria_comparativo.png")
plt.close()

### TIMEOUT

# Contagem de timeouts por n_itens para cada algoritmo
branch_timeout_por_itens = branch_df[branch_df["timeout"]].groupby("n_itens").size()
fptas_timeout_por_itens = fptas_df[fptas_df["timeout"]].groupby("n_itens").size()
greedy_timeout_por_itens = greedy_df[greedy_df["tempo_seg"] >= 1800].groupby("n_itens").size()

todos_n_itens = sorted(set(branch_df["n_itens"].dropna()) |
                       set(fptas_df["n_itens"].dropna()) |
                       set(greedy_df["n_itens"].dropna()))

# Reindexar com todos os n_itens, preenchendo com 0 onde necessário
branch_timeout_por_itens = branch_timeout_por_itens.reindex(todos_n_itens, fill_value=0)
fptas_timeout_por_itens = fptas_timeout_por_itens.reindex(todos_n_itens, fill_value=0)
greedy_timeout_por_itens = greedy_timeout_por_itens.reindex(todos_n_itens, fill_value=0)

# Combinar em DataFrame único
df_heatmap = pd.DataFrame({
    "Branch and Bound": branch_timeout_por_itens,
    "FPTAS": fptas_timeout_por_itens,
    "Greedy": greedy_timeout_por_itens
}).T 

# Agrupar colunas com n_itens <= 100
df_heatmap_grouped = df_heatmap.copy()
df_heatmap_grouped.columns = df_heatmap_grouped.columns.map(lambda x: "≤ 100" if x <= 100 else x)
df_heatmap_grouped = df_heatmap_grouped.groupby(level=0, axis=1).sum() # type: ignore

# Ordenar colunas
colunas_ordenadas = ["≤ 100"] + sorted([c for c in df_heatmap_grouped.columns if c != "≤ 100"])
df_heatmap_grouped = df_heatmap_grouped[colunas_ordenadas]

# Plotar heatmap
plt.figure(figsize=(12, 4))
sns.heatmap(df_heatmap_grouped, annot=True, fmt="d", cmap="Reds", linewidths=0.5, cbar_kws={'label': 'Quantidade de Timeouts'})
plt.title("Heatmap de Timeouts por Algoritmo e Número de Itens", fontsize=14)
plt.xlabel("Número de Itens")
plt.ylabel("Algoritmo")
plt.tight_layout()
plt.savefig("imagens/heatmap_timeouts.png")
plt.close()