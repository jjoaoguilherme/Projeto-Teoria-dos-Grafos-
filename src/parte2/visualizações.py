"""[IA] Codex – figuras de desempenho a partir dos tempos exportados."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
from statistics import stdev

from .verificar_experimentos import verificar_relatorio

CORES = {'BFS': '#2563eb', 'DFS': '#0f766e',
         'DIJKSTRA': '#b45309', 'BELLMAN_FORD': '#7c3aed'}


def preparar_series(dados):
    """Agrupa somente tarefas com a mesma ordem e tamanho de grafo."""
    verificacao = verificar_relatorio(dados)
    if not verificacao['valido']:
        raise ValueError('; '.join(verificacao['erros']))
    grupos = defaultdict(list)
    for item in dados['experimentos']:
        identificacao = item.get('identificacao', {})
        tarefa = identificacao.get('caso') or item['tarefa']
        destino = identificacao.get('destino')
        rotulo = f"{item['algoritmo']} · {item['origem']}"
        if destino is not None:
            rotulo += f' → {destino}'
        if identificacao.get('caso'):
            rotulo += f' · {tarefa}'
        tempos = item['tempos_segundos']
        grupos[(item['vertices'], item['arestas'])].append({
            'rotulo': rotulo, 'algoritmo': item['algoritmo'],
            'media': item['tempo_medio_segundos'], 'desvio': stdev(tempos),
            'tempos': list(tempos), 'repeticoes': item['repeticoes'],
        })
    return dict(sorted(grupos.items()))


def gerar_graficos(arquivo='out/parte2/parte2_report.json', pasta='out/parte2/graficos'):
    """Exporta PNG e SVG; barras são médias, pontos são tempos individuais.

    Grupos de mesmo tamanho podem ter origens, pesos e tarefas distintos;
    não agrega tarefas nem classifica um algoritmo como melhor.
    """
    dados = json.loads(Path(arquivo).read_text(encoding='utf-8-sig'))
    grupos = preparar_series(dados)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch

    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    saidas = []
    with plt.rc_context({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'axes.spines.top': False, 'axes.spines.right': False}):
        for (vertices, arestas), series in grupos.items():
            # Unidade menor apenas para tornar os recortes rápidos legíveis.
            fator, unidade = (1e6, 'µs') if max(s['media'] for s in series) < 0.001 else (1, 's')
            figura, eixo = plt.subplots(figsize=(12, max(4.4, len(series) * .55 + 2)))
            for indice, serie in enumerate(series):
                cor = CORES[serie['algoritmo']]
                eixo.barh(indice, serie['media'] * fator, color=cor, alpha=.78,
                          xerr=serie['desvio'] * fator, capsize=3,
                          error_kw={'ecolor': '#374151', 'linewidth': 1})
                deslocamentos = [(i - (len(serie['tempos'])-1)/2) * .035
                                  for i in range(len(serie['tempos']))]
                eixo.scatter([t * fator for t in serie['tempos']],
                             [indice + d for d in deslocamentos], color='#111827',
                             s=15, alpha=.65, zorder=3)
            eixo.set_yticks(range(len(series)), [s['rotulo'] for s in series])
            eixo.invert_yaxis()
            eixo.set_xlim(left=0)
            eixo.set_xlabel(f'Tempo de execução ({unidade})')
            eixo.set_ylabel('Algoritmo e tarefa')
            eixo.set_title(f'Desempenho por tarefa — {vertices:,} vértices | {arestas:,} arcos',
                           loc='left', fontweight='bold', pad=14)
            eixo.grid(axis='x', alpha=.15)
            eixo.set_axisbelow(True)
            legenda = [Patch(facecolor=CORES[a], label=a)
                       for a in dict.fromkeys(s['algoritmo'] for s in series)]
            legenda += [Line2D([], [], marker='o', color='#111827', linestyle='',
                               label='Execuções individuais'),
                        Line2D([], [], color='#374151', marker='|',
                               label='±1 desvio-padrão amostral')]
            figura.legend(handles=legenda, loc='lower center', ncol=3, frameon=False)
            repeticoes = ', '.join(map(str, sorted({s['repeticoes'] for s in series})))
            figura.text(.02, .12,
                        f'Barras: média de {repeticoes} execuções por tarefa. '
                        'Origens e transformações de pesos podem diferir.\n'
                        f'Fonte: {Path(arquivo).name}. Escalas independentes entre figuras.',
                        fontsize=9, color='#4b5563')
            figura.tight_layout(rect=(0, .19, 1, 1))
            for formato in ('png', 'svg'):
                destino = pasta / f'desempenho_v{vertices}_e{arestas}.{formato}'
                figura.savefig(destino, dpi=180, facecolor='white')
                saidas.append(destino)
            plt.close(figura)
    return saidas


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--arquivo', default='out/parte2/parte2_report.json')
    parser.add_argument('--out', default='out/parte2/graficos')
    args = parser.parse_args()
    try:
        for arquivo in gerar_graficos(args.arquivo, args.out):
            print(arquivo)
    except (ValueError, OSError) as erro:
        parser.exit(1, f'Erro: {erro}\n')


if __name__ == '__main__':
    main()
