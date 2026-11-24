"""[IA] Codex – gráficos de escalabilidade dos quatro algoritmos."""
import argparse
import json
from pathlib import Path
from statistics import stdev

from .verificar_experimentos import verificar_relatorio
from .experimentos import ALGORITMOS


def preparar_escalabilidade(dados):
    """Exige a mesma origem e seleção de vértices por tamanho nos quatro casos."""
    verificacao = verificar_relatorio(dados)
    if not verificacao['valido']:
        raise ValueError('; '.join(verificacao['erros']))
    series = {nome: [] for nome in ALGORITMOS}
    assinatura = None
    amostras = {}
    for item in dados['experimentos']:
        identificacao = item.get('identificacao', {})
        if identificacao.get('caso') != 'ESCALABILIDADE':
            raise ValueError('Use somente o relatório de escalabilidade.')
        metadados = identificacao.get('amostragem', {})
        atual = (item['origem'], identificacao.get('sha256'),
                 identificacao.get('limite_vertices'), metadados.get('semente'))
        if assinatura is None:
            assinatura = atual
        if atual != assinatura:
            raise ValueError('Não misture origens, bases, limites ou sementes.')
        if (metadados.get('vertices'), metadados.get('arestas')) != (item['vertices'], item['arestas']):
            raise ValueError('Tamanho do experimento difere dos metadados da amostra.')
        vertices = item['vertices']
        assinatura_amostra = json.dumps(metadados, sort_keys=True)
        if vertices in amostras and amostras[vertices] != assinatura_amostra:
            raise ValueError('Amostras diferentes com o mesmo tamanho.')
        amostras[vertices] = assinatura_amostra
        series[item['algoritmo']].append(item)
    for itens in series.values():
        itens.sort(key=lambda e: e['vertices'])
        tamanhos = [e['vertices'] for e in itens]
        if len(tamanhos) < 3 or len(set(tamanhos)) != len(tamanhos):
            raise ValueError('Cada algoritmo deve ter pelo menos três tamanhos distintos, sem duplicatas.')
        if tamanhos != sorted(amostras):
            raise ValueError('Os quatro algoritmos devem usar os mesmos tamanhos.')
    return series


def gerar_graficos(arquivo='out/parte2/escalabilidade_report.json', pasta='out/parte2/graficos'):
    dados = json.loads(Path(arquivo).read_text(encoding='utf-8-sig'))
    series = preparar_escalabilidade(dados)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from importlib import import_module
    cores = import_module('src.parte2.visualizações').CORES
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    figura, eixos = plt.subplots(2, 2, figsize=(12, 8), sharex=True)
    for eixo, (nome, itens) in zip(eixos.flat, series.items()):
        eixo.errorbar([e['vertices'] for e in itens],
                      [e['tempo_medio_segundos'] for e in itens],
                      yerr=[stdev(e['tempos_segundos']) for e in itens],
                      color=cores[nome], marker='o', capsize=4, label='Média ±1 desvio-padrão')
        for item in itens:
            eixo.annotate(f"E={item['arestas']}",
                          (item['vertices'], item['tempo_medio_segundos']),
                          xytext=(0, 10), textcoords='offset points', ha='center', fontsize=8)
        eixo.set_title(nome)
        eixo.set_xlabel('Vértices da amostra (V)')
        eixo.set_ylabel('Tempo de execução (s)')
        teto = max(e['tempo_medio_segundos'] + stdev(e['tempos_segundos']) for e in itens)
        eixo.set_ylim(0, teto * 1.25 if teto else 1)
        eixo.margins(x=.15, y=.3)
        eixo.grid(alpha=.2)
        eixo.legend(fontsize=8)
    figura.suptitle('Escalabilidade por algoritmo', fontsize=17, fontweight='bold')
    figura.text(.03, .02, 'E indica os arcos de cada amostra. Escalas verticais independentes.\n'
                'Dijkstra usa 2 − LINK_SENTIMENT; os demais mantêm os pesos originais. '
                f'Fonte: {Path(arquivo).name}.', fontsize=9)
    figura.tight_layout(rect=(0, .08, 1, .95))
    saidas = [pasta / f'escalabilidade.{ext}' for ext in ('png', 'svg')]
    for destino in saidas:
        figura.savefig(destino, dpi=180, facecolor='white')
    plt.close(figura)
    return saidas


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--arquivo', default='out/parte2/escalabilidade_report.json')
    parser.add_argument('--out', default='out/parte2/graficos')
    args = parser.parse_args()
    try:
        for arquivo in gerar_graficos(args.arquivo, args.out):
            print(arquivo)
    except (OSError, ValueError) as erro:
        parser.exit(1, f'Erro: {erro}\n')


if __name__ == '__main__':
    main()
