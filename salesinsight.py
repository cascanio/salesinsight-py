# RF01 – Criar ou Carregar o Dataset de Vendas (Consuelo)

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def gerar_dataset_vendas(n_registros=200, seed=42):
    """Gera um dataset sintético de vendas com dados intencionalmente sujos."""
    random.seed(seed)
    np.random.seed(seed)

    produtos = ["Notebook", "Smartphone", "Tablet", "Monitor", "Teclado", "Mouse", "Headset"]
    categorias = {"Notebook": "Computadores", "Smartphone": "Celulares", "Tablet": "Celulares",
                  "Monitor": "Computadores", "Teclado": "Periféricos", "Mouse": "Periféricos",
                  "Headset": "Periféricos"}
    regioes = ["Sudeste", "Sul", "Nordeste", "Centro-Oeste", "Norte"]
    clientes = [f"Cliente_{i:03d}" for i in range(1, 51)]

    data_inicio = datetime(2024, 1, 1)
    dados = []

    for i in range(n_registros):
        produto = random.choice(produtos)
        quantidade = random.randint(1, 10)
        preco_base = {"Notebook": 3500, "Smartphone": 2200, "Tablet": 1800,
                      "Monitor": 1200, "Teclado": 250, "Mouse": 120, "Headset": 350}[produto]
        preco = round(preco_base * random.uniform(0.85, 1.15), 2)
        data = data_inicio + timedelta(days=random.randint(0, 364))

        # Inserindo dados intencionalmente sujos para limpeza
        if random.random() < 0.05:
            quantidade = None          # valor nulo
        if random.random() < 0.04:
            preco = None               # valor nulo
        if random.random() < 0.03:
            produto = "  " + produto   # espaço extra (string suja)

        dados.append({
            "id_venda": i + 1,
            "data_venda": data.strftime("%Y-%m-%d") if random.random() > 0.02 else "DATA INVÁLIDA",
            "cliente": random.choice(clientes),
            "produto": produto,
            "categoria": categorias.get(produto.strip(), "Outros"),
            "regiao": random.choice(regioes),
            "quantidade": quantidade,
            "preco_unitario": preco
        })

    return pd.DataFrame(dados)

# Gerar e salvar
df_bruto = gerar_dataset_vendas()
df_bruto.to_csv("vendas.csv", index=False)
print(f"Dataset gerado com {len(df_bruto)} registros.")
print(df_bruto.head())

# RF02 – Inspecionar e Descrever os Dados (Consuelo)

def inspecionar_dados(df):
    """Exibe informações básicas do DataFrame."""
    print("\n=== INSPEÇÃO INICIAL DO DATASET ===")
    print(f"Shape: {df.shape}")
    print(f"\nColunas: {list(df.columns)}")
    print(f"\nTipos de dados:\n{df.dtypes}")
    print(f"\nValores nulos por coluna:\n{df.isnull().sum()}")
    print(f"\nPrimeiros registros:\n{df.head()}")
    print(f"\nEstatísticas descritivas:\n{df.describe()}")


inspecionar_dados(df_bruto)

#RF03 – Limpar e Tratar os Dados (Consuelo)

import re

def limpar_dados(df):
    """
    Limpa e trata o DataFrame de vendas.
    Retorna o DataFrame limpo e um relatório de limpeza.
    """
    n_inicial = len(df)
    relatorio = {}

    # 1. Remover espaços extras em colunas de texto
    colunas_texto = df.select_dtypes(include="object").columns
    for col in colunas_texto:
        df[col] = df[col].str.strip()

    # 2. Converter data e remover datas inválidas
    df["data_venda"] = pd.to_datetime(df["data_venda"], errors="coerce")
    n_datas_invalidas = df["data_venda"].isnull().sum()
    df = df.dropna(subset=["data_venda"])
    relatorio["datas_invalidas_removidas"] = n_datas_invalidas

    # 3. Remover linhas com quantidade ou preço nulos
    n_antes = len(df)
    df = df.dropna(subset=["quantidade", "preco_unitario"])
    relatorio["linhas_nulas_removidas"] = n_antes - len(df)

    # 4. Garantir tipos numéricos corretos
    df["quantidade"] = df["quantidade"].astype(int)
    df["preco_unitario"] = df["preco_unitario"].astype(float)


    n_final = len(df)
    relatorio["registros_iniciais"] = n_inicial
    relatorio["registros_finais"] = n_final
    relatorio["registros_removidos_total"] = n_inicial - n_final

    print("\n=== RELATÓRIO DE LIMPEZA ===")
    for chave, valor in relatorio.items():
        print(f"  {chave}: {valor}")

    return df, relatorio


# RF04  → RF05 → RF06 → RF07 → RF11 → RF12 (Leon Emiliano)

# RF04 – Criar Colunas Derivadas com Transformações

def criar_colunas_derivadas(df):
    """Cria colunas calculadas e derivadas a partir do dataset limpo."""

    # Receita total por linha de venda
    df["receita_total"] = df["quantidade"] * df["preco_unitario"]

    # Extração de componentes de data
    df["mes"] = df["data_venda"].dt.month
    df["mes_nome"] = df["data_venda"].dt.strftime("%B")  # nome do mês
    df["trimestre"] = df["data_venda"].dt.quarter.apply(lambda q: f"Q{q}")
    df["ano"] = df["data_venda"].dt.year

    # Classificação da receita por item com numpy.select (transformação condicional vetorizada)
    condicoes = [
        df["receita_total"] < 500,
        (df["receita_total"] >= 500) & (df["receita_total"] < 5000),
        df["receita_total"] >= 5000
    ]
    classificacoes = ["Baixo Valor", "Médio Valor", "Alto Valor"]
    df["faixa_receita_item"] = np.select(condicoes, classificacoes, default="Não Classificado")

    print("\n=== COLUNAS DERIVADAS CRIADAS ===")
    print(df[["data_venda", "receita_total", "mes", "trimestre", "faixa_receita_item"]].head())

    return df

# RF05 – Calcular Métricas Agregadas (groupby)

def calcular_metricas(df):
    """Calcula e retorna métricas agregadas do dataset."""
    metricas = {}

    # Receita por mês
    por_mes = df.groupby("mes").agg(
        receita_total=("receita_total", "sum"),
        quantidade=("quantidade", "sum"),
        n_vendas=("id_venda", "count")
    ).reset_index().sort_values("mes")
    metricas["por_mes"] = por_mes

    # Top 5 produtos por receita
    top_produtos = df.groupby("produto")["receita_total"].sum()\
                     .sort_values(ascending=False).head(5).reset_index()
    metricas["top_produtos"] = top_produtos

    # Receita por categoria
    por_categoria = df.groupby("categoria")["receita_total"].sum().reset_index()
    metricas["por_categoria"] = por_categoria

    # Receita por região
    por_regiao = df.groupby("regiao").agg(
        receita_total=("receita_total", "sum"),
        media_ticket=("receita_total", "mean")
    ).reset_index().sort_values("receita_total", ascending=False)
    metricas["por_regiao"] = por_regiao

    # Exibição
    for nome, tabela in metricas.items():
        print(f"\n=== {nome.upper().replace('_', ' ')} ===")
        print(tabela.to_string(index=False))

    return metricas

# RF06 – Segmentar Clientes por Nível de Gasto

def segmentar_clientes(df):
    """Segmenta clientes pelo total gasto usando groupby e lambda."""

    clientes = df.groupby("cliente")["receita_total"].sum().reset_index()
    clientes.columns = ["cliente", "total_gasto"]

    # Classificação usando função lambda com condicionais
    clientes["segmento"] = clientes["total_gasto"].apply(
        lambda gasto: "Ouro" if gasto > 15000
                      else ("Prata" if gasto >= 5000 else "Bronze")
    )

    clientes = clientes.sort_values("total_gasto", ascending=False)

    print("\n=== SEGMENTAÇÃO DE CLIENTES ===")
    print(clientes.head(10).to_string(index=False))
    print(f"\nDistribuição de segmentos:\n{clientes['segmento'].value_counts()}")

    return clientes

# RF07 – Calcular Estatísticas com NumPy

def calcular_estatisticas_numpy(df):
    """Usa NumPy para calcular estatísticas sobre as receitas."""
    print("\n=== ESTATÍSTICAS COM NUMPY ===")

    receitas = df["receita_total"].to_numpy()  # Converte para array NumPy

    media = np.mean(receitas)
    mediana = np.median(receitas)
    desvio_padrao = np.std(receitas)
    total = np.sum(receitas)
    p25 = np.percentile(receitas, 25)
    p75 = np.percentile(receitas, 75)

    print(f"  Receita média por venda:    R$ {media:.2f}")
    print(f"  Receita mediana por venda:  R$ {mediana:.2f}")
    print(f"  Desvio padrão:              R$ {desvio_padrao:.2f}")
    print(f"  Receita total:              R$ {total:.2f}")
    print(f"  Percentil 25 (Q1):          R$ {p25:.2f}")
    print(f"  Percentil 75 (Q3):          R$ {p75:.2f}")

    # Broadcasting: normalizar receitas entre 0 e 1
    receitas_normalizadas = (receitas - receitas.min()) / (receitas.max() - receitas.min())
    print(f"\n  Receitas normalizadas (primeiros 5): {receitas_normalizadas[:5].round(4)}")

    # Operação vetorizada: identificar vendas acima da média sem loop
    acima_da_media = receitas[receitas > media]
    print(f"\n  Vendas acima da média: {len(acima_da_media)} de {len(receitas)}")

    return {
        "media": media, "mediana": mediana,
        "desvio_padrao": desvio_padrao, "total": total
    }
# RF11 – Usar Funções Lambda e Funções de Ordem Superior

def executar_callback(df, callback):
    return callback(df)

total = executar_callback(
    df_limpo,
    lambda df: df["receita_total"].sum()
)

print(f"Receita total: R$ {total:,.2f}")

def processar_coluna(df, coluna, funcao_transformacao):
    """
    Aplica uma função de transformação a uma coluna do DataFrame.
    Demonstra o uso de funções como argumentos (higher-order function / callback).
    """
    df_limpo[f"{coluna}_transformado"] = df_limpo[coluna].apply(funcao_transformacao)
    print(f"  Coluna '{coluna}_transformado' criada com sucesso.")
    return df

# Uso da função com lambda como callback
df_limpo = processar_coluna(df_limpo, "receita_total", lambda x: round(x / 1000, 2))
df_limpo = processar_coluna(df_limpo, "quantidade", lambda x: "Alto" if x > 5 else "Baixo")


# RF12 – Ler e Escrever Arquivos (CSV e JSON)

import json

def exportar_resultados(metricas, clientes, stats_numpy):
    """Exporta resultados em CSV e JSON."""
    os.makedirs("outputs", exist_ok=True)

    # Exportar CSV com métricas por mês
    caminho_csv = "outputs/metricas_por_mes.csv"
    metricas["por_mes"].to_csv(caminho_csv, index=False, encoding="utf-8-sig")
    print(f"  CSV exportado: {caminho_csv}")

    # Exportar segmentação de clientes em CSV
    caminho_clientes = "outputs/segmentacao_clientes.csv"
    clientes.to_csv(caminho_clientes, index=False, encoding="utf-8-sig")
    print(f"  CSV exportado: {caminho_clientes}")

    # Exportar estatísticas gerais em JSON
    caminho_json = "outputs/estatisticas_gerais.json"
    stats_serializaveis = {k: round(float(v), 2) for k, v in stats_numpy.items()}
    with open(caminho_json, "w", encoding="utf-8") as f:
        json.dump(stats_serializaveis, f, indent=4, ensure_ascii=False)
    print(f"  JSON exportado: {caminho_json}")

    # Ler e exibir o JSON exportado para confirmar
    with open(caminho_json, "r", encoding="utf-8") as f:
        dados_lidos = json.load(f)
    print(f"\n  Conteúdo do JSON exportado:\n  {json.dumps(dados_lidos, indent=2)}")

# RF13 – Usar Expressões Regulares para Limpeza de Dados (Consuelo)

import re

def limpar_strings_com_regex(df):
    """
    Usa expressões regulares para limpeza de colunas de texto.
    Exemplos: remover caracteres especiais, padronizar formatos.
    """

    # 1. Remover caracteres não alfanuméricos do nome do cliente (exceto underline e espaço)
    df["cliente_limpo"] = df["cliente"].apply(
        lambda s: re.sub(r"[^a-zA-Z0-9_ ]", "", str(s)).strip()
    )

    # 2. Identificar registros com padrão de ID inválido (deve ser "Cliente_XXX")
    padrao_cliente = re.compile(r"^Cliente_\d{3}$")
    df["cliente_valido"] = df["cliente_limpo"].apply(
        lambda s: bool(padrao_cliente.match(s))
    )

    n_invalidos = (~df["cliente_valido"]).sum()
    print(f"\n=== LIMPEZA COM REGEX ===")
    print(f"  Clientes com formato inválido encontrados: {n_invalidos}")
    print(f"  Amostra de clientes limpos: {df['cliente_limpo'].head(5).tolist()}")

    return df

