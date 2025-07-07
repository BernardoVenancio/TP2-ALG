import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Criar pasta de imagens
os.makedirs("imagens", exist_ok=True)

def carregar_capacidades(label_dirs):
    capacidades = {}
    for pasta in label_dirs:
        for nome_arquivo in os.listdir(pasta):
            if nome_arquivo.endswith(".csv"):
                caminho = os.path.join(pasta, nome_arquivo)
                with open(caminho, 'r') as f:
                    linhas = f.readlines()
                    for linha in linhas:
                        if linha.startswith("c,"): 
                            capacidade = int(linha.strip().split(",")[1]) 
                            break
                nome_instancia = nome_arquivo.replace(".csv", "")
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


def load_datasets_bnb():
    datasets_bnb = {
        "branch_large_linear": pd.read_csv("resultados/bnb/large_linear.csv"),
        "branch_low_linear": pd.read_csv("resultados/bnb/low_linear.csv"),
        "branch_large_constant": pd.read_csv("resultados/bnb/large_constant.csv"),
        "branch_low_constant": pd.read_csv("resultados/bnb/low_constant.csv"),
    }
    return datasets_bnb


data_bnb = load_datasets_bnb()


branch_linear_df = pd.concat([data_bnb["branch_large_linear"], data_bnb["branch_low_linear"]], ignore_index=True)
branch_constant_df = pd.concat([data_bnb["branch_large_constant"], data_bnb["branch_low_constant"]], ignore_index=True)

# Adicionar a capacidade aos dataframes
branch_linear_df = adicionar_capacidade(branch_linear_df)
branch_constant_df = adicionar_capacidade(branch_constant_df)

# Filtrando apenas as instâncias que aparecem no constant
instancias_com_tempo_constant = branch_constant_df["instancia"].unique()
branch_linear_df_filtrado = branch_linear_df[branch_linear_df["instancia"].isin(instancias_com_tempo_constant)]

# Adicionando a coluna 'tipo_bound' para distinguir entre Linear e Constant
branch_linear_df_filtrado.loc[:, "tipo_bound"] = "Linear"  
branch_constant_df.loc[:, "tipo_bound"] = "Constant"  

# Verificando dados antes de gerar o gráfico
print("Verificando dados do Linear:")
print(branch_linear_df_filtrado[["capacidade_mochila", "tempo_seg", "tipo_bound"]].head())
print("Verificando dados do Constant:")
print(branch_constant_df[["capacidade_mochila", "tempo_seg", "tipo_bound"]].head())

# Verificando se há valores nulos
print("Verificando valores nulos no Linear:")
print(branch_linear_df_filtrado[["capacidade_mochila", "tempo_seg", "tipo_bound"]].isnull().sum())
print("Verificando valores nulos no Constant:")
print(branch_constant_df[["capacidade_mochila", "tempo_seg", "tipo_bound"]].isnull().sum())

# Remover valores nulos de 'capacidade_mochila' e 'tempo_seg' 
branch_linear_df_filtrado = branch_linear_df_filtrado.dropna(subset=["capacidade_mochila", "tempo_seg"])
branch_constant_df = branch_constant_df.dropna(subset=["capacidade_mochila", "tempo_seg"])
# Filtrando os dados onde a capacidade da mochila é maior que 2000
branch_linear_df_filtrado_2000 = branch_linear_df_filtrado[branch_linear_df_filtrado["capacidade_mochila"] > 2000]
branch_constant_df_2000 = branch_constant_df[branch_constant_df["capacidade_mochila"] > 2000]

# Concatenando os dois dataframes filtrados
dados_filtrados = pd.concat([branch_linear_df_filtrado_2000, branch_constant_df_2000])


#############


branch_linear_df_filtrado_500 = branch_linear_df_filtrado[branch_linear_df_filtrado["n_itens"] <= 500]
branch_constant_df_500 = branch_constant_df[branch_constant_df["n_itens"] <= 500]


dados_filtrados_500 = pd.concat([branch_linear_df_filtrado_500, branch_constant_df_500])


plt.figure(figsize=(10, 6))


sns.scatterplot(
    x="capacidade_mochila", 
    y="n_nos", 
    hue="tipo_bound", 
    style="tipo_bound",  
    data=dados_filtrados_500,
    palette="Set1",  
    s=100,  
)


plt.yscale('log')  


plt.title("Número de Nós por Capacidade da Mochila (≤ 500 Itens)")
plt.xlabel("Capacidade da Mochila")
plt.ylabel("Número de Nós (Escala Logarítmica)")
plt.legend(title="Tipo de Bound", loc="upper left")


plt.savefig("imagens/nos_por_capacidade_500_itens.png")



plt.figure(figsize=(10, 6))


sns.scatterplot(
    x="capacidade_mochila", 
    y="n_fila", 
    hue="tipo_bound", 
    style="tipo_bound",  
    data=dados_filtrados_500,
    palette="Set1",  
    s=100,  
)


plt.yscale('log')  


plt.title("Tamanho da Fila Máxima por Capacidade da Mochila (≤ 500 Itens)")
plt.xlabel("Capacidade da Mochila")
plt.ylabel("Tamanho da Fila Máxima (Escala Logarítmica)")
plt.legend(title="Tipo de Bound", loc="upper left")


plt.savefig("imagens/tamanho_fila_por_capacidade_500_itens.png")


plt.figure(figsize=(10, 6))


sns.scatterplot(
    x="capacidade_mochila", 
    y="tempo_seg", 
    hue="tipo_bound", 
    style="tipo_bound",  
    data=dados_filtrados_500,
    palette="Set1",  
    s=100,  
)


plt.yscale('log')  


plt.title("Tempo de Execução por Capacidade da Mochila (≤ 500 Itens)")
plt.xlabel("Capacidade da Mochila")
plt.ylabel("Tempo de Execução (Escala Logarítmica)")
plt.legend(title="Tipo de Bound", loc="upper left")


plt.savefig("imagens/tempo_execucao_por_capacidade_500_itens.png")
