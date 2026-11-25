import pandas as pd
from pathlib import Path

raiz_projeto = Path(__file__).resolve().parents[2]
caminho_dataset = raiz_projeto / "out" / "parte2" / "base_avd.csv"
pasta_resultados = raiz_projeto / "out" / "parte2" / "avd"
pasta_resultados.mkdir(parents=True, exist_ok=True)

# Carregar o dataset original, sem modificá-lo.
df_original = pd.read_csv(caminho_dataset)
df_original["TIMESTAMP"] = pd.to_datetime(df_original["TIMESTAMP"])

print("=== DATASET ORIGINAL ===")
print("Data inicial:", df_original["TIMESTAMP"].min())
print("Data final:", df_original["TIMESTAMP"].max())
print("Total de registros:", len(df_original))

# Recorte de pesquisa definido pelo grupo: 01/01/2014 em diante.
df = df_original.loc[
    df_original["TIMESTAMP"] >= pd.Timestamp("2014-01-01")
].copy()

print("\n=== RECORTE DA PESQUISA ===")
print("Data inicial:", df["TIMESTAMP"].min())
print("Data final:", df["TIMESTAMP"].max())
print("Registros utilizados:", len(df))
print("Registros fora do recorte:", len(df_original) - len(df))

print("\nDistribuição geral de sentimentos:")
print(df["LINK_SENTIMENT"].value_counts())

todas_comunidades = (
    set(df["SOURCE_SUBREDDIT"]) | set(df["TARGET_SUBREDDIT"])
)
print("\nTotal de comunidades:", len(todas_comunidades))

comunidades_alvo = ["ps4", "xboxone"]
meses = pd.date_range(
    start=pd.Timestamp("2014-01-01"),
    end=df["TIMESTAMP"].max().to_period("M").to_timestamp(),
    freq="MS",
)

linhas_estruturais = []
linhas_sentimentos = []
linhas_relacionais = []
linhas_estatisticas = []
linhas_iqr = []
linhas_candidatos_iqr = []


# sentimento por mês/direção e distribuição de referências por comunidade conectada.
linhas_sentimentos_mensais = []
linhas_comunidades_conectadas = []
linhas_frequencia_conexoes = []

for comunidade in comunidades_alvo:
    feitas = df.loc[df["SOURCE_SUBREDDIT"] == comunidade]
    recebidas = df.loc[df["TARGET_SUBREDDIT"] == comunidade]

    print(f"\n{'=' * 45}")
    print(f"Comunidade: {comunidade}")
    print(f"{'=' * 45}")

    # Análise estrutural já definida pelo grupo.
    destinos_distintos = feitas["TARGET_SUBREDDIT"].nunique()
    origens_distintas = recebidas["SOURCE_SUBREDDIT"].nunique()

    print("Referências feitas:", len(feitas))
    print("Referências recebidas:", len(recebidas))
    print("Comunidades para as quais fez referências:", destinos_distintos)
    print("Comunidades das quais recebeu referências:", origens_distintas)

    linhas_estruturais.append({
        "COMUNIDADE": comunidade,
        "REFERENCIAS_FEITAS": len(feitas),
        "REFERENCIAS_RECEBIDAS": len(recebidas),
        "DESTINOS_DISTINTOS": destinos_distintos,
        "ORIGENS_DISTINTAS": origens_distintas,
    })

    # Análise distribucional: mesmas contagens e percentuais já calculados.
    for direcao, dados in [("Feitas", feitas), ("Recebidas", recebidas)]:
        quantidades = dados["LINK_SENTIMENT"].value_counts().reindex(
            [-1, 1], fill_value=0
        )
        percentuais = (
            quantidades.div(len(dados)).mul(100).round(2)
            if len(dados)
            else quantidades.astype(float)
        )

        print(f"\nSentimentos - referências {direcao.lower()} (quantidades):")
        print(quantidades)
        print(f"\nSentimentos - referências {direcao.lower()} (percentuais):")
        print(percentuais)

        for sentimento in [-1, 1]:
            linhas_sentimentos.append({
                "COMUNIDADE": comunidade,
                "DIRECAO": direcao,
                "LINK_SENTIMENT": sentimento,
                "DESCRICAO": (
                    "Negativo" if sentimento == -1 else "Neutro ou positivo"
                ),
                "QUANTIDADE": int(quantidades.loc[sentimento]),
                "PERCENTUAL": float(percentuais.loc[sentimento]),
            })

    # Análise temporal, incluindo meses com zero registros.
    feitas_por_mes = feitas.groupby(
        pd.Grouper(key="TIMESTAMP", freq="MS")
    ).size().reindex(meses, fill_value=0)

    recebidas_por_mes = recebidas.groupby(
        pd.Grouper(key="TIMESTAMP", freq="MS")
    ).size().reindex(meses, fill_value=0)

    assert feitas_por_mes.sum() == len(feitas), (
        "Erro na soma das referências feitas!"
    )
    assert recebidas_por_mes.sum() == len(recebidas), (
        "Erro na soma das referências recebidas!"
    )
    assert len(feitas_por_mes) == len(meses)
    assert len(recebidas_por_mes) == len(meses)

    print("\nValidação temporal: OK")
    print("Meses analisados:", len(meses))

    tabela_mensal = pd.DataFrame({
        "MES": meses,
        "REFERENCIAS_FEITAS": feitas_por_mes.to_numpy(),
        "REFERENCIAS_RECEBIDAS": recebidas_por_mes.to_numpy(),
    })
    tabela_mensal.to_csv(
        pasta_resultados / f"mensal_{comunidade}.csv",
        index=False,
        date_format="%Y-%m-%d",
        encoding="utf-8-sig",
    )
 
    # Exportar sentimento por mês e comunidade conectada.
    for direcao, dados, serie_mensal, coluna_parceiro in [
        ("Feitas", feitas, feitas_por_mes, "TARGET_SUBREDDIT"),
        ("Recebidas", recebidas, recebidas_por_mes, "SOURCE_SUBREDDIT"),
    ]:
        # O mês recebe uma data padronizada: primeiro dia do mês.
        dados_com_mes = dados.assign(
            MES=dados["TIMESTAMP"].dt.to_period("M").dt.to_timestamp()
        )
        quantidades_mensais = (
            dados_com_mes.groupby(["MES", "LINK_SENTIMENT"])
            .size()
            .unstack(fill_value=0)
            .reindex(index=meses, columns=[-1, 1], fill_value=0)
        )

        # O cruzamento por sentimento deve reproduzir a série mensal original.
        assert (
            quantidades_mensais.sum(axis=1).to_numpy()
            == serie_mensal.to_numpy()
        ).all(), f"Inconsistência temporal no sentimento: {comunidade}/{direcao}"

        for mes, quantidades in quantidades_mensais.iterrows():
            total_mes = int(quantidades.sum())
            for sentimento in [-1, 1]:
                quantidade = int(quantidades.loc[sentimento])
                linhas_sentimentos_mensais.append({
                    "COMUNIDADE": comunidade,
                    "DIRECAO": direcao,
                    "MES": mes.strftime("%Y-%m-%d"),
                    "LINK_SENTIMENT": sentimento,
                    "QUANTIDADE": quantidade,
                    # Sem registros no mês, o percentual é indefinido (CSV vazio).
                    "PERCENTUAL": round(100 * quantidade / total_mes, 2)
                    if total_mes else None,
                })

        # Cada par de comunidades pode conter várias referências no dataset.
        contagens_parceiros = (
            dados.groupby([coluna_parceiro, "LINK_SENTIMENT"])
            .size()
            .unstack(fill_value=0)
            .reindex(columns=[-1, 1], fill_value=0)
        )
        total_por_parceiro = contagens_parceiros.sum(axis=1)

        assert int(total_por_parceiro.sum()) == len(dados), (
            f"Inconsistência nas comunidades conectadas: {comunidade}/{direcao}"
        )

        for parceiro, quantidade_total in total_por_parceiro.items():
            negativas = int(contagens_parceiros.loc[parceiro, -1])
            neutras_positivas = int(contagens_parceiros.loc[parceiro, 1])
            linhas_comunidades_conectadas.append({
                "COMUNIDADE": comunidade,
                "DIRECAO": direcao,
                "COMUNIDADE_CONECTADA": parceiro,
                "REFERENCIAS": int(quantidade_total),
                "NEGATIVAS": negativas,
                "NEUTRAS_OU_POSITIVAS": neutras_positivas,
            })

        # Frequência de comunidades conectadas por quantidade de referências.
        frequencias = total_por_parceiro.value_counts().sort_index()
        assert int(sum(qtd * num for qtd, num in frequencias.items())) == len(dados)
        for referencias, qtd_comunidades in frequencias.items():
            linhas_frequencia_conexoes.append({
                "COMUNIDADE": comunidade,
                "DIRECAO": direcao,
                "REFERENCIAS_POR_COMUNIDADE": int(referencias),
                "QTD_COMUNIDADES": int(qtd_comunidades),
            })

    # Estatísticas mensais e diagnóstico IQR já presentes no analisador.
    for direcao, serie in [
        ("Feitas", feitas_por_mes),
        ("Recebidas", recebidas_por_mes),
    ]:
        estatisticas = serie.describe()
        print(f"\n--- Estatísticas mensais: {comunidade} - {direcao} ---")
        print(estatisticas)
        print("\nCinco maiores contagens mensais:")
        print(serie.nlargest(5))

        linhas_estatisticas.append({
            "COMUNIDADE": comunidade,
            "DIRECAO": direcao,
            "MESES": int(estatisticas["count"]),
            "MEDIA": estatisticas["mean"],
            "DESVIO_PADRAO": estatisticas["std"],
            "MINIMO": estatisticas["min"],
            "Q1": estatisticas["25%"],
            "MEDIANA": estatisticas["50%"],
            "Q3": estatisticas["75%"],
            "MAXIMO": estatisticas["max"],
        })

        q1 = serie.quantile(0.25)
        q3 = serie.quantile(0.75)
        iqr = q3 - q1
        limite_inferior = q1 - 1.5 * iqr
        limite_superior = q3 + 1.5 * iqr
        candidatos = serie[(serie < limite_inferior) | (serie > limite_superior)]

        print("\n--- Diagnóstico IQR ---")
        print("Q1:", q1)
        print("Q3:", q3)
        print("IQR:", iqr)
        print("Limite inferior:", limite_inferior)
        print("Limite superior:", limite_superior)
        print("Possíveis outliers:", len(candidatos))
        if candidatos.empty:
            print("Nenhum valor fora dos limites.")
        else:
            print(candidatos)

        linhas_iqr.append({
            "COMUNIDADE": comunidade,
            "DIRECAO": direcao,
            "Q1": q1,
            "Q3": q3,
            "IQR": iqr,
            "LIMITE_INFERIOR": limite_inferior,
            "LIMITE_SUPERIOR": limite_superior,
            "QTD_CANDIDATOS": len(candidatos),
        })
        for mes, quantidade in candidatos.items():
            linhas_candidatos_iqr.append({
                "COMUNIDADE": comunidade,
                "DIRECAO": direcao,
                "MES": mes.strftime("%Y-%m-%d"),
                "QUANTIDADE": int(quantidade),
            })

    # Análise relacional já definida pelo grupo.
    dados_comparacao = pd.concat([
        feitas.assign(DIRECAO="Feitas"),
        recebidas.assign(DIRECAO="Recebidas"),
    ], ignore_index=True)

    tabela_relacional = pd.crosstab(
        dados_comparacao["DIRECAO"],
        dados_comparacao["LINK_SENTIMENT"],
        normalize="index",
    ).mul(100).round(2).reindex(
        index=["Feitas", "Recebidas"], columns=[-1, 1], fill_value=0
    )

    print("\nTabela relacional - direção x sentimento:")
    print(tabela_relacional)

    for direcao in ["Feitas", "Recebidas"]:
        linhas_relacionais.append({
            "COMUNIDADE": comunidade,
            "DIRECAO": direcao,
            "PCT_NEGATIVO": float(tabela_relacional.loc[direcao, -1]),
            "PCT_NEUTRO_OU_POSITIVO": float(tabela_relacional.loc[direcao, 1]),
        })

# Qualidade dos dados do recorte.
print("\n=== QUALIDADE DOS DADOS ===")
ausentes = df.isna().sum()
print("\nValores ausentes:")
print(ausentes)

post_ids_repetidos = int(df["POST_ID"].duplicated().sum())
colunas_registro = [
    "SOURCE_SUBREDDIT", "TARGET_SUBREDDIT", "POST_ID",
    "TIMESTAMP", "LINK_SENTIMENT",
]
registros_identicos = int(df.duplicated(subset=colunas_registro).sum())
sentimentos_invalidos = int((~df["LINK_SENTIMENT"].isin([-1, 1])).sum())

print("\nPOST_ID repetidos:", post_ids_repetidos)
print("Registros idênticos:", registros_identicos)
print("Sentimentos inválidos:", sentimentos_invalidos)


def exportar(nome, registros, colunas=None):
    pd.DataFrame(registros, columns=colunas).to_csv(
        pasta_resultados / nome, index=False, encoding="utf-8-sig"
    )


exportar("sentimento_mensal.csv", linhas_sentimentos_mensais)
exportar("comunidades_conectadas.csv", linhas_comunidades_conectadas)
exportar("frequencia_referencias_por_comunidade.csv", linhas_frequencia_conexoes)

exportar("resumo_estrutural.csv", linhas_estruturais)
exportar("sentimentos.csv", linhas_sentimentos)
exportar("relacao_direcao_sentimento.csv", linhas_relacionais)
exportar("estatisticas_mensais.csv", linhas_estatisticas)
exportar("diagnostico_iqr.csv", linhas_iqr)
exportar(
    "candidatos_iqr.csv", linhas_candidatos_iqr,
    colunas=["COMUNIDADE", "DIRECAO", "MES", "QUANTIDADE"],
)

linhas_qualidade = [
    {"VERIFICACAO": "VALORES_AUSENTES", "COLUNA": col, "QUANTIDADE": int(qtd)}
    for col, qtd in ausentes.items()
]
linhas_qualidade.extend([
    {"VERIFICACAO": "POST_ID_REPETIDOS", "COLUNA": "POST_ID", "QUANTIDADE": post_ids_repetidos},
    {"VERIFICACAO": "REGISTROS_IDENTICOS", "COLUNA": "", "QUANTIDADE": registros_identicos},
    {"VERIFICACAO": "SENTIMENTOS_INVALIDOS", "COLUNA": "LINK_SENTIMENT", "QUANTIDADE": sentimentos_invalidos},
])
exportar("qualidade_dados.csv", linhas_qualidade)

print("\n=== ARQUIVOS EXPORTADOS ===")
for arquivo in sorted(pasta_resultados.glob("*.csv")):
    print(arquivo.relative_to(raiz_projeto))
