
# RF09 – Criar uma Classe para o Pipeline

class AnalisadorDeVendas:
    """
    Classe responsável por encapsular o pipeline de análise de vendas.
    Mantém o estado do DataFrame e os resultados intermediários.
    """

    def __init__(self, caminho_arquivo):
        """Inicializa o analisador com o caminho do arquivo de dados."""
        self.caminho_arquivo = caminho_arquivo
        self.df_bruto = None
        self.df_limpo = None
        self.metricas = {}
        self.clientes = None
        self.relatorio_limpeza = {}

    def carregar(self):
        """Lê o arquivo CSV e armazena o DataFrame bruto."""
        self.df_bruto = pd.read_csv(self.caminho_arquivo)
        print(f"[AnalisadorDeVendas] Arquivo carregado: {self.caminho_arquivo}")
        print(f"  Registros carregados: {len(self.df_bruto)}")
        return self

    def limpar(self):
        """Limpa os dados e armazena o DataFrame tratado."""
        self.df_limpo, self.relatorio_limpeza = limpar_dados(self.df_bruto.copy())
        return self

    def transformar(self):
        """Aplica transformações e cria colunas derivadas."""
        self.df_limpo = criar_colunas_derivadas(self.df_limpo)
        return self

    def analisar(self):
        """Calcula métricas e segmentações."""
        self.metricas = calcular_metricas(self.df_limpo)
        self.clientes = segmentar_clientes(self.df_limpo)
        calcular_estatisticas_numpy(self.df_limpo)
        return self

    def visualizar(self):
        """Gera e exporta os gráficos."""
        gerar_visualizacoes(self.df_limpo, self.metricas)
        return self

    def exportar_relatorio(self, caminho="outputs/relatorio_resumo.csv"):
        """Exporta o relatório de métricas por mês em CSV."""
        os.makedirs("outputs", exist_ok=True)
        self.metricas["por_mes"].to_csv(caminho, index=False)
        print(f"\n[AnalisadorDeVendas] Relatório exportado: {caminho}")
        return self

    def resumo(self):
        """Exibe um resumo executivo do pipeline."""
        print("\n" + "="*50)
        print("       RESUMO EXECUTIVO – SALESINSIGHT PY")
        print("="*50)
        print(f"  Arquivo analisado:      {self.caminho_arquivo}")
        print(f"  Registros brutos:       {self.relatorio_limpeza.get('registros_iniciais', 'N/A')}")
        print(f"  Registros limpos:       {self.relatorio_limpeza.get('registros_finais', 'N/A')}")
        receita = self.df_limpo["receita_total"].sum() if self.df_limpo is not None else 0
        print(f"  Receita total anual:    R$ {receita:,.2f}")
        if self.clientes is not None:
            top = self.clientes.iloc[0]
            print(f"  Cliente top:            {top['cliente']} (R$ {top['total_gasto']:,.2f})")
        print("="*50)

# RF10 – Usar Herança

class AnalisadorComProjecao(AnalisadorDeVendas):
    """
    Extensão do AnalisadorDeVendas com funcionalidades de projeção simples.
    Herda todos os métodos da classe pai e adiciona projeção de tendência.
    """

    def __init__(self, caminho_arquivo, meses_projecao=3):
        super().__init__(caminho_arquivo)
        self.meses_projecao = meses_projecao
        self.projecoes = []

    def projetar_tendencia(self):
        """
        Projeta a receita dos próximos meses com base na média móvel dos últimos 3 meses.
        Método simples sem machine learning – baseado em médias.
        """
        if not self.metricas or "por_mes" not in self.metricas:
            print("[AVISO] Rode .analisar() antes de projetar.")
            return self

        por_mes = self.metricas["por_mes"].sort_values("mes")
        receitas_historicas = por_mes["receita_total"].to_numpy()

        # Média móvel dos últimos 3 meses como base da projeção
        ultimos_3 = receitas_historicas[-3:]
        media_movel = np.mean(ultimos_3)
        tendencia = np.std(ultimos_3) * 0.1  # fator de crescimento simples

        ultimo_mes = int(por_mes["mes"].max())

        print("\n=== PROJEÇÃO DE TENDÊNCIA (Média Móvel Simples) ===")
        print(f"  Base: média dos últimos 3 meses = R$ {media_movel:,.2f}")
        self.projecoes = []

        for i in range(1, self.meses_projecao + 1):
            mes_projetado = (ultimo_mes + i - 1) % 12 + 1
            receita_projetada = media_movel + (tendencia * i)
            self.projecoes.append({"mes": mes_projetado, "receita_projetada": round(receita_projetada, 2)})
            print(f"  Mês {mes_projetado:02d} (projeção): R$ {receita_projetada:,.2f}")

        return self

    def exibir_projecao_detalhada(self):
        """Exibe as projeções calculadas."""
        if not self.projecoes:
            print("[AVISO] Nenhuma projeção disponível. Rode .projetar_tendencia() primeiro.")
            return
        print("\n=== DETALHAMENTO DAS PROJEÇÕES ===")
        for p in self.projecoes:
            print(f"  Mês {p['mes']:02d}: R$ {p['receita_projetada']:,.2f}")

# RF14 – Executar o Pipeline Completo (Ponto de Entrada)

def main():
    """
    Função principal: executa o pipeline completo do SalesInsight PY.
    """
    print("\n" + "="*60)
    print("   SALESINSIGHT PY – Pipeline de Análise de Dados de Vendas")
    print("="*60)

    # Etapa 0: Gerar dataset (se necessário)
    if not os.path.exists("vendas.csv"):
        print("\n[INFO] Gerando dataset sintético...")
        df_gerado = gerar_dataset_vendas(n_registros=200)
        df_gerado.to_csv("vendas.csv", index=False)

    # Etapa 1 a 6: Pipeline via classe com herança
    analisador = AnalisadorComProjecao("vendas.csv", meses_projecao=3)
    (analisador
        .carregar()
        .limpar()
        .transformar()
        .analisar()
        .projetar_tendencia()
        .visualizar()
        .exportar_relatorio()
    )

    # Etapa extra: limpeza com regex
    analisador.df_limpo = limpar_strings_com_regex(analisador.df_limpo)

    # Etapa extra: exportação JSON
    stats = calcular_estatisticas_numpy(analisador.df_limpo)
    exportar_resultados(analisador.metricas, analisador.clientes, stats)

    # Resumo final
    analisador.resumo()
    analisador.exibir_projecao_detalhada()

    print("\n[CONCLUÍDO] Pipeline finalizado com sucesso!")


if __name__ == "__main__":
    main()
