# 📊 SalesInsight PY

> Pipeline completo de análise de dados de vendas desenvolvido em Python puro — do dataset bruto ao relatório exportado.

---

## 📌 Sobre o projeto

O **SalesInsight PY** é um sistema de análise de dados de vendas que cobre todas as etapas de um pipeline real:
geração e carregamento de dados, inspeção, limpeza, transformação, agregação, segmentação, estatísticas,
visualização e exportação de relatórios. O projeto foi desenvolvido como exercício prático dos conceitos
do **Módulo 01 de IA para Análise Preditiva**.

---

## 🔍 O que o sistema analisa

- Geração de dataset sintético com dados intencionalmente sujos (nulos, espaços extras, datas inválidas)
- Inspeção inicial: shape, tipos, nulos e estatísticas descritivas
- Limpeza automatizada com relatório de registros removidos
- Criação de colunas derivadas: receita total, mês, trimestre, faixa de valor
- Receita total e volume de vendas por mês
- Top 5 produtos por receita
- Desempenho por categoria e por região (ticket médio incluído)
- Segmentação de clientes por nível de gasto: **Bronze**, **Prata** e **Ouro**
- Estatísticas com NumPy: média, mediana, desvio padrão, percentis e normalização
- Projeção de tendência por média móvel simples para os próximos meses
- Limpeza de strings com expressões regulares
- Exportação de relatórios em **CSV** e **JSON**
- Visualizações em PNG: linha de receita mensal, barras de top produtos e boxplot por região

---

## 🎯 Objetivo

Praticar os principais conceitos do Módulo 01 de IA para Análise Preditiva:

- Lógica de programação com Python
- Variáveis, tipos de dados e operadores
- Condicionais (`if`, `elif`, `else`) e repetição (`for`, `while`)
- Funções, parâmetros, retorno e **funções lambda**
- **Funções de ordem superior** (função que recebe função como argumento / callbacks)
- Leitura e escrita de arquivos **CSV** e **JSON**
- Módulo `datetime` para manipulação e extração de componentes de datas
- **Expressões regulares** com o módulo `re` para validação e limpeza de strings
- **Pandas**: DataFrames, `groupby`, `agg`, `apply`, filtros, limpeza e transformações
- **NumPy**: arrays, operações vetorizadas, broadcasting, `np.select`, percentis e normalização
- **Matplotlib** e **Seaborn**: gráficos de linha, barras, boxplot, customização e exportação em PNG
- **Classes** com construtor `__init__`, atributos de instância, métodos e encadeamento de chamadas
- **Herança** com `super()`: `AnalisadorComProjecao` extende `AnalisadorDeVendas`
- GitHub, branches, commits e GitFlow simplificado
- Kanban no GitHub Projects para organização do projeto

---

## ⚙️ Como executar

### ☁️ No Google Colab (recomendado)

1. Faça upload do arquivo `salesinsight.py` para o ambiente Colab.
2. Execute diretamente no terminal do Colab:
   ```
   !python salesinsight.py
   ```
3. Ou cole o conteúdo em células de um notebook `.ipynb` e execute célula a célula.

> O dataset `vendas.csv` é gerado automaticamente pelo próprio script caso não exista.

---

### 💻 Localmente com VS Code

1. Instale o **Python 3.10+** e o **VS Code**.
2. Clone o repositório ou baixe os arquivos.
3. Instale as dependências:
   ```
   pip install pandas numpy matplotlib seaborn
   ```
4. Execute no terminal:
   ```
   python salesinsight.py
   ```

---

## 🗂️ Estrutura do projeto

```
salesinsight-py/
│
├── salesinsight.py              # Pipeline principal (RF01 a RF14)
├── vendas.csv                   # Dataset gerado automaticamente
├── README.md                    # Este arquivo
│
└── outputs/
    ├── metricas_por_mes.csv         # Receita e volume agregados por mês
    ├── segmentacao_clientes.csv     # Clientes com total gasto e segmento
    ├── relatorio_resumo.csv         # Relatório exportado pela classe
    ├── estatisticas_gerais.json     # Estatísticas NumPy em JSON
    │
    └── graficos/
        ├── vendas_por_mes.png           # Gráfico de linha: receita mensal
        ├── top_produtos.png             # Barras horizontais: top 5 produtos
        └── distribuicao_regioes.png     # Boxplot: receita por região
```

---

## 🏗️ Arquitetura do pipeline

O pipeline segue uma arquitetura orientada a objetos com encadeamento de métodos:

```
gerar_dataset_vendas()
        ↓
AnalisadorComProjecao("vendas.csv")
        ↓
  .carregar()       → lê o CSV com pd.read_csv
        ↓
  .limpar()         → remove nulos, datas inválidas, corrige tipos
        ↓
  .transformar()    → cria colunas: receita_total, mes, trimestre, faixa_receita
        ↓
  .analisar()       → groupby por mês/produto/região/cliente + NumPy stats
        ↓
  .projetar_tendencia()  → média móvel dos últimos 3 meses
        ↓
  .visualizar()     → 3 gráficos exportados em PNG
        ↓
  .exportar_relatorio()  → CSV com métricas por mês
        ↓
exportar_resultados()    → CSV de clientes + JSON de estatísticas
```

---

## 🧰 Ferramentas utilizadas

| Categoria           | Ferramenta / Biblioteca                        |
|---------------------|-----------------------------------------------|
| Linguagem           | Python 3.10+                                  |
| Ambiente            | Google Colab / VS Code                        |
| Manipulação de dados| `pandas`, `numpy`                             |
| Visualização        | `matplotlib`, `seaborn`                       |
| Utilitários Python  | `re`, `json`, `datetime`, `os`, `random`      |
| Versionamento       | Git + GitHub + GitHub Desktop                 |
| Gestão de tarefas   | GitHub Projects (Kanban)                      |

---

## 🧩 Conceitos-chave ilustrados no código

### Funções lambda e de ordem superior
```python
# Função que recebe outra função como argumento (higher-order function)
def executar_callback(df, callback):
    return callback(df)

total = executar_callback(df_limpo, lambda df: df["receita_total"].sum())

# Lambda aplicada com apply() para segmentação de clientes
clientes["segmento"] = clientes["total_gasto"].apply(
    lambda gasto: "Ouro" if gasto > 15000 else ("Prata" if gasto >= 5000 else "Bronze")
)
```

### Classes e herança com super()
```python
class AnalisadorDeVendas:
    def __init__(self, caminho_arquivo):
        self.caminho_arquivo = caminho_arquivo
        ...

class AnalisadorComProjecao(AnalisadorDeVendas):
    def __init__(self, caminho_arquivo, meses_projecao=3):
        super().__init__(caminho_arquivo)   # chama o construtor da classe pai
        self.meses_projecao = meses_projecao
```

### NumPy vetorizado com np.select
```python
condicoes = [
    df["receita_total"] < 500,
    (df["receita_total"] >= 500) & (df["receita_total"] < 5000),
    df["receita_total"] >= 5000
]
classificacoes = ["Baixo Valor", "Médio Valor", "Alto Valor"]
df["faixa_receita_item"] = np.select(condicoes, classificacoes)
```

### Expressões regulares para validação
```python
padrao_cliente = re.compile(r"^Cliente_\d{3}$")
df["cliente_valido"] = df["cliente_limpo"].apply(
    lambda s: bool(padrao_cliente.match(s))
)
```

---

## 🌐 Sobre variáveis em Python vs JavaScript

Em Python, não existe a distinção entre `var`, `let` e `const` como no JavaScript.
Toda variável é declarada com simples atribuição (`=`). Por convenção, constantes são
escritas em MAIÚSCULAS (ex.: `N_REGISTROS = 200`).
Para simular imutabilidade real, pode-se usar **tuplas** no lugar de listas.

---

## 🌍 Como os dados circulam (contexto real)

Neste projeto os dados são lidos de um arquivo local CSV gerado sinteticamente.
Em produção, esses dados poderiam vir de uma **API REST** — o script faria uma
requisição HTTP GET para um servidor que retorna JSON, seguindo a arquitetura
**cliente-servidor**. A biblioteca `requests` do Python permite consumir essas APIs
com poucas linhas de código.

---

## 👥 Autores e divisão de responsabilidades

| Requisito | Responsável   | Descrição                                      |
|-----------|---------------|------------------------------------------------|
| RF01      | Consuelo      | Geração e carregamento do dataset              |
| RF02      | Consuelo      | Inspeção inicial dos dados                     |
| RF03      | Consuelo      | Limpeza e tratamento dos dados                 |
| RF04–RF12 | Leon Emiliano | Transformações, métricas, classes, exportação  |
| RF13      | Consuelo      | Limpeza de strings com regex                   |
| RF14      | Leon Emiliano | Função `main()` — ponto de entrada do pipeline |

---

## 🎬 Vídeo de demonstração

https://www.youtube.com/watch?v=9H5qan0FaGQ

---

## 🔗 Repositório

https://github.com/cascanio/salesinsight-py

---

> Projeto desenvolvido como parte do **Módulo 01 – IA para Análise Preditiva**.
