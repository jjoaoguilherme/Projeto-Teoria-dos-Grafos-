# IA Chatgpt: apoio na utilização da biblioteca matplotlib e correção de erros

# Geração das seis visualizações de AVD com Matplotlib.

# Lê os resultados previamente produzidos por estudo_global.py.

from __future__ import annotations


import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ESTRATOS = ["grau_0", "grau_1", "grau_2_10", "grau_11_100", "grau_acima_100"]
ROTULOS = ["0", "1", "2 a 10", "11 a 100", ">100"]
AZUL, TEAL, LARANJA = "#3168a5", "#008b82", "#c66b3d"


def estilo():
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 10,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.titleweight": "bold", "axes.titlesize": 13,
        "axes.labelsize": 10, "figure.dpi": 120,
        "savefig.dpi": 180, "axes.grid": False,
    })


def exportar(fig, caminho: Path):
    fig.tight_layout(pad=1.8)
    fig.savefig(caminho.with_suffix(".png"), bbox_inches="tight", facecolor="white")
    fig.savefig(caminho.with_suffix(".svg"), bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Gerado: {caminho.with_suffix('.png')}")


def rotulo_barras(ax, barras, digitos=0, sufixo=""):
    for b in barras:
        valor = b.get_height()
        if digitos == 0:
            texto = f"{valor:,.0f}".replace(",", ".")
        else:
            texto = f"{valor:.{digitos}f}".replace(".", ",")
        ax.annotate(f"{texto}{sufixo}", (b.get_x()+b.get_width()/2, valor),
                    xytext=(0, 4), textcoords="offset points", ha="center",
                    va="bottom", fontsize=9)


def faixa(grau):
    return np.select(
        [grau.eq(0), grau.eq(1), grau.between(2,10), grau.between(11,100), grau.gt(100)],
        ESTRATOS, default="invalido"
    )


def figura_1(comunidades, saida):
    """Exploratória: distribuição EXATA das comunidades pelos estratos."""
    estratos = faixa(comunidades["vizinhos_saida"])
    contagens = pd.Series(estratos).value_counts().reindex(ESTRATOS, fill_value=0)

    fig, ax = plt.subplots(figsize=(9.2, 5.0))

    barras = ax.bar(ROTULOS, contagens.values,color=AZUL, width=.66,label="Comunidades por faixa de grau de saída")

    ax.set(title="Comunidades por número de destinos distintos",
           xlabel="Destinos distintos por comunidade (grau de saída simples)",
           ylabel="Quantidade de comunidades")
    
    ax.set_ylim(0, contagens.max()*1.16)
    ax.grid(axis="y", color="#e4e8eb", zorder=0)
    ax.set_axisbelow(True)

    rotulo_barras(ax, barras)

    ax.legend(
        loc="upper right",
        frameon=False,
        fontsize=9)

    exportar(fig, saida/"01_exploratoria_distribuicao_estratos")


def figura_2(comunidades, saida):
    """Exploratoria: concentracao EXATA de referencias de saida na rede completa.

    Todas as 54.075 comunidades participam, inclusive as sem referencias de saida.
    Ordenacao decrescente (curva de concentracao), nao uma curva de Lorenz.
    """
    referencias = pd.to_numeric(comunidades["referencias_saida"], errors="raise")
    if referencias.isna().any() or (referencias < 0).any() or referencias.sum() <= 0:
        raise ValueError("Contagens de referencias de saida invalidas.")
    total = len(referencias)
    valores = np.sort(referencias.to_numpy(dtype=float))[::-1]
    x = np.r_[0.0, 100.0 * np.arange(1, total + 1) / total]
    y = np.r_[0.0, 100.0 * np.cumsum(valores) / valores.sum()]
    def parcela_top(p):
        k = int(np.ceil(total * p / 100))
        return 100.0 * np.sum(valores[:k]) / np.sum(valores)
    um = parcela_top(1)
    dez = parcela_top(10)

    fig, ax = plt.subplots(figsize=(10, 5.4))
    ax.fill_between(x, y, x, color=AZUL, alpha=.09)
    ax.plot(x, y, color=AZUL, lw=2.4, label="Distribuicao observada")
    ax.plot([0, 100], [0, 100], "--", color="#8f969e", lw=1.4,
            label="Referencia: distribuicao igualitaria")
    ax.scatter([1, 10], [um, dez], s=45, color=LARANJA, zorder=4)
    ax.plot([1,1], [0,um], color=LARANJA, ls=":", lw=1.1)
    ax.text(27, 59, f"Top 1% das comunidades: {um:.1f}% das referencias".replace(".", ","),
            fontsize=10, color="#263644", weight="bold")
    ax.text(27, 52, f"Top 10%: {dez:.1f}% das referencias".replace(".", ","),
            fontsize=10, color="#263644")
    ax.set(title="Concentracao das referencias de saida por comunidade",
           xlabel="Comunidades acumuladas, da maior para a menor (%)",
           ylabel="Referencias de saida acumuladas (%)", xlim=(0,100),ylim=(0,103))
    ax.grid(axis="both", color="#e4e8eb", alpha=.75)
    ax.set_axisbelow(True)
    ax.legend(loc="lower right", frameon=False, fontsize=9)
    fig.text(.5, .01, "Censo de 54.075 comunidades; referencias repetidas contam separadamente.",
             ha="center", fontsize=9, color="#555")
    exportar(fig, saida/"02_exploratoria_concentracao_referencias")


def figura_3(amostra, saida):
    """Exploratória multivariada: sentimento e alcance, separados por estrato.

    Usa apenas as 384 origens sorteadas (não a população completa).
    Agrupa pares de percentuais arredondados a 0,1 ponto percentual
    para representar sobreposições por meio do tamanho das bolhas.
    Não aplica correlação inferencial nem presume causalidade.
    """
    colunas = ["origem", "estrato", "proporcao_negativas_saida", "proporcao_alcance"]
    faltantes = [c for c in colunas if c not in amostra.columns]
    if faltantes:
        raise ValueError(f"Amostra sem colunas necessárias à figura 3: {faltantes}")

    d = amostra[colunas].copy()

    for coluna in ("proporcao_negativas_saida", "proporcao_alcance"):
        d[coluna] = pd.to_numeric(d[coluna], errors="coerce")

    if d[["proporcao_negativas_saida", "proporcao_alcance"]].isna().any().any():
        raise ValueError(
            "Há valores indefinidos na amostra para a figura 3; revisar antes de desenhar."
        )

    if (
        d[["proporcao_negativas_saida", "proporcao_alcance"]].lt(0)
        | d[["proporcao_negativas_saida", "proporcao_alcance"]].gt(1)
    ).any().any():
        raise ValueError(
            "As proporções de sentimento e alcance devem estar em [0, 1]."
        )

    estratos = ESTRATOS[1:]
    if set(d["estrato"]) != set(estratos):
        raise ValueError("Estratos inesperados ou ausentes na amostra analítica.")

    if d["origem"].duplicated().any():
        raise ValueError("A amostra contém origens repetidas.")

    nomes = [
        "1 destino distinto",
        "2 a 10 destinos",
        "11 a 100 destinos",
        "Mais de 100 destinos"
    ]

    fig, axs = plt.subplots(2, 2, figsize=(11, 7.6), sharex=True, sharey=True)

    for ax, estrato, nome in zip(axs.flat, estratos, nomes):
        parte = d.loc[d["estrato"].eq(estrato)].copy()

        # Percentuais exibidos com resolução de 0,1 p.p. para tornar as sobreposições visíveis.
        parte["negativas_pct"] = (100 * parte["proporcao_negativas_saida"]).round(1)
        parte["alcance_pct"] = (100 * parte["proporcao_alcance"]).round(1)

        pontos = (
            parte.groupby(["negativas_pct", "alcance_pct"], as_index=False)
            .size()
            .rename(columns={"size": "origens_no_ponto"})
        )

        tamanhos = 24 + 44 * np.sqrt(pontos["origens_no_ponto"].to_numpy())

        ax.scatter(
            pontos["negativas_pct"],
            pontos["alcance_pct"],
            s=tamanhos,
            facecolor=AZUL,
            edgecolor="white",
            linewidth=.7,
            alpha=.72
        )

        ax.set(
            title=f"{nome} (n={len(parte)})",
            xlim=(-3, 103),
            ylim=(-3, 49)
        )
        ax.grid(alpha=.25, color="#aeb9c1")
        ax.set_axisbelow(True)
        ax.set_xticks([0, 25, 50, 75, 100])
        ax.set_yticks([0, 10, 20, 30, 40])

    # Título geral e eixos
    fig.suptitle(
        "Sentimento negativo e alcançabilidade por faixa de conectividade",
        fontweight="bold",
        fontsize=14,
        y=.985
    )
    fig.supxlabel("Referências negativas de saída (%)", y=.075)
    fig.supylabel("Outras comunidades alcançáveis (%)", x=.032)

    # Legenda de tamanho das bolhas
    exemplos = [1, 2, 4, 8]
    handles = [
        plt.scatter(
            [], [], 
            s=24 + 44 * np.sqrt(v),
            facecolor=AZUL,
            edgecolor="white",
            linewidth=.7,
            alpha=.72
        )
        for v in exemplos
    ]

    fig.legend(
        handles,
        [f"{v} origem{'ens' if v > 1 else ''}" for v in exemplos],
        title="Sobreposição no ponto",
        loc="lower center",
        bbox_to_anchor=(0.5, 0.035),
        ncol=4,
        frameon=False,
        fontsize=8.5,
        title_fontsize=9
    )

    fig.text(
        .5, .008,
        "384 origens amostradas; bolhas maiores indicam mais origens sobrepostas no mesmo par de percentuais. "
        "Percentuais exibidos com arredondamento de 0,1 ponto percentual; análise descritiva, sem inferência causal.",
        ha="center",
        fontsize=8.2,
        color="#555"
    )

    fig.subplots_adjust(bottom=0.19, top=0.90, wspace=0.16, hspace=0.22)

    exportar(fig, saida / "03_exploratoria_sentimento_alcance_estrato")



def figura_4(comunidades, saida):
    """Exploratória: participação em ciclos negativos recíprocos por estrato."""
    d = comunidades.copy()
    d["estrato"] = faixa(d["vizinhos_saida"])
    d["em_ciclo"] = d["em_ciclo_negativo_duas_arestas"].astype(str).str.lower().eq("true")

    tab = d.groupby("estrato")["em_ciclo"].agg(["sum", "count"]).reindex(ESTRATOS)
    pct = (100 * tab["sum"] / tab["count"]).to_numpy(dtype=float)

    fig, ax = plt.subplots(figsize=(10.3, 5.2))
    y = np.arange(len(ROTULOS))[::-1]

    ax.hlines(y, 0, pct, color="#c9d9d5", lw=3.5, zorder=1)

    ax.scatter(
        pct, y,
        s=110,
        color=TEAL,
        edgecolor="white",
        linewidth=1.2,
        zorder=3,
        label="Participação em ciclo negativo recíproco"
    )

    for yy, value in zip(y, pct):
        ax.annotate(
            f"{value:.2f}%".replace(".", ","),
            (value, yy),
            xytext=(9, 0),
            textcoords="offset points",
            va="center",
            fontsize=10
        )

    ax.set_yticks(y, ROTULOS)
    ax.set(
        xlim=(-2, 67),
        ylim=(-.65, 4.65),
        title="Comunidades em ciclos negativos de duas arestas",
        xlabel="Comunidades do estrato que participam do ciclo (%)",
        ylabel="Destinos distintos por comunidade"
    )

    ax.grid(axis="x", color="#e4e8eb", alpha=.85)
    ax.set_axisbelow(True)

    # Legenda da figura
    ax.legend(
        loc="upper right",
        frameon=False,
        fontsize=9
    )

    fig.text(
        .5, .01,
        "Censo das 54.075 comunidades; ciclos de duas arestas negativas recíprocas.",
        ha="center",
        fontsize=9,
        color="#555"
    )

    exportar(fig, saida / "04_exploratoria_ciclos_lollipop")


def figura_5(amostra, estimativa, saida):
    """Explanatória: observações da amostra + médias por estrato.

    O grau zero é mostrado à parte como valor exato, nunca como uma observação
    amostral inventada. Para os demais estratos, pontos observados da amostra.
    """
    fig, ax = plt.subplots(figsize=(11.5, 6.0))
    rng = np.random.default_rng(42)  # jitter de apresentação, sem alterar valores
    ordem = ESTRATOS[1:]
    dados = [100 * pd.to_numeric(amostra.loc[amostra.estrato.eq(e), "proporcao_alcance"]) for e in ordem]
    if any(len(v) == 0 or v.isna().any() for v in dados):
        raise ValueError("Estrato amostral ausente ou com alcançabilidade indefinida")

    # Primeira posição: censo exato de grau zero.
    ax.scatter([0], [0], s=105, marker="D", color="#777e85", edgecolor="white", zorder=6,
               label="Valor exato (grau 0)")
    ax.annotate("0,00% (censo)", (0, 0), xytext=(0, 14), textcoords="offset points",
                ha="center", fontsize=9, color="#555")

    for i, valores in enumerate(dados, start=1):
        valores = valores.to_numpy(dtype=float)
        xs = i + rng.uniform(-.25, .25, len(valores))
        ax.scatter(xs, valores, s=22, alpha=.22, color=AZUL, linewidth=0,
                   label="Origens amostradas" if i == 1 else None, zorder=2)
        media = float(valores.mean())
        ax.scatter([i], [media], marker="D", s=95, color=LARANJA,
                   edgecolor="white", linewidth=1, zorder=5,
                   label="Média amostral" if i == 1 else None)
        ax.annotate(f"{media:.2f}%".replace(".", ","), (i, media),
                    xytext=(0, -17), textcoords="offset points",
                    ha="center", va="top", color="#8f441c", weight="bold", fontsize=9)

    ax.set_xticks(range(5), ROTULOS)
    ax.set(title="Distribuição da alcançabilidade das origens por faixa de grau",
           xlabel="Destinos distintos por comunidade",
           ylabel="Outras comunidades alcançáveis (%)",
           xlim=(-.5, 4.5), ylim=(-3.8, 50))
    ax.grid(axis="y", color="#e4e8eb", alpha=.8)
    ax.set_axisbelow(True)
    ax.legend(loc="center right", frameon=False, fontsize=9)
    fig.text(.5, .01, "Grau 0: valor exato. Quatro demais faixas: 384 origens sorteadas; pontos com deslocamento horizontal visual.",
             ha="center", fontsize=8.5, color="#555")
    exportar(fig, saida / "05_explanatoria_alcance_distribuicao")


def figura_6(amostra, N, saida):
    """Explanatória: comparativo pareado das médias antes e depois.

    Alcance após remoção de arestas negativas = alcance original - perda.
    Eixo x ampliado (34–46%): cuidado ao interpretar magnitude visual.
    """
    cols = ["proporcao_alcance", "perda_alcance_remocao_negativas"]
    if any(c not in amostra.columns for c in cols):
        raise ValueError(f"Amostra não possui {cols}")
    d = amostra.copy()
    d["original_pct"] = 100 * pd.to_numeric(d["proporcao_alcance"], errors="raise")
    d["sem_negativas_pct"] = d["original_pct"] - 100 * pd.to_numeric(
        d["perda_alcance_remocao_negativas"], errors="raise") / (N - 1)
    if d[["original_pct", "sem_negativas_pct"]].isna().any().any():
        raise ValueError("Amostra com porcentagem de alcance indefinida")
    if (d["sem_negativas_pct"] < -1e-9).any():
        raise ValueError("Perda maior que alcance original")
    tab = d.groupby("estrato")[["original_pct", "sem_negativas_pct"]].mean().reindex(ESTRATOS[1:])
    if tab.isna().any().any():
        raise ValueError("Estratos faltantes")

    fig, ax = plt.subplots(figsize=(11, 5.6))
    y = np.arange(4)[::-1]
    original = tab["original_pct"].to_numpy()
    sem = tab["sem_negativas_pct"].to_numpy()
    for yy, p, s in zip(y, original, sem):
        ax.plot([s, p], [yy, yy], color="#8698a3", lw=3.5, zorder=1)
        ax.annotate(f"−{(p-s):.2f}".replace(".", ",") + " p.p.", (p, yy),
                    xytext=(11, 0), textcoords="offset points", va="center",
                    fontsize=9.5, color="#47545d")
    ax.scatter(original, y, color=AZUL, s=100, edgecolor="white", linewidth=.9,
               label="Grafo original", zorder=4)
    ax.scatter(sem, y, color=LARANJA, s=100, edgecolor="white", linewidth=.9,
               label="Sem referências negativas", zorder=4)
    ax.set_yticks(y, ROTULOS[1:])
    ax.set(title="Alcançabilidade média antes e depois da remoção de referências negativas",
           xlabel="Outras comunidades alcançáveis (%)",
           ylabel="Destinos distintos por comunidade",
           xlim=(32, 48), ylim=(-.6, 3.6))
    ax.grid(axis="x", color="#e4e8eb", alpha=.85)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, fontsize=9, loc="lower left")
    fig.text(.5, .01, "Mesmas 384 origens amostrais. Eixo horizontal ampliado: não começa em zero. Diferenças em pontos percentuais.",
             ha="center", fontsize=8.5, color="#555")
    exportar(fig, saida / "06_explanatoria_antes_depois_negativas")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base",type=Path,default=Path("out/parte2/global_amostragem_v2"))
    parser.add_argument("--out",type=Path,default=Path("out/parte2/figuras_avd"))
    args=parser.parse_args()
    base, saida = args.base,args.out
    saida.mkdir(parents=True,exist_ok=True)
    estilo()
    com = pd.read_csv(base/"globais/comunidades.csv",keep_default_na=False)
    amostra = pd.read_csv(base/"amostra_analitica.csv",keep_default_na=False)
    estimativa=json.loads((base/"estimativa_media_alcance.json").read_text(encoding="utf-8"))
    N=len(com)
    if N < 2: raise ValueError("A análise requer pelo menos duas comunidades.")
    figura_1(com,saida)
    figura_2(com,saida)
    figura_3(amostra,saida)
    figura_4(com,saida)
    figura_5(amostra,estimativa,saida)
    figura_6(amostra,N,saida)
    print(f"Concluído. Figuras em: {saida}")


if __name__=="__main__":
    main()
