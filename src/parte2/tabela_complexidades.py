"""[IA] Codex – tabela numérica de apoio à comparação com custos assintóticos."""
import argparse
import csv
import json
from math import log2
from pathlib import Path
from statistics import stdev

from .graficos_escalabilidade import preparar_escalabilidade


def gerar_tabela(arquivo='out/parte2/escalabilidade_report.json',
                 destino='out/parte2/comparacao_complexidades.csv'):
    series = preparar_escalabilidade(json.loads(Path(arquivo).read_text(encoding='utf-8-sig')))
    linhas = []
    for nome, itens in series.items():
        referencia_tempo, referencia_fator = None, None
        for item in itens:
            v, e = item['vertices'], item['arestas']
            formula = ('V+E' if nome in ('BFS', 'DFS') else
                       'V+E+E*log2(E+1)' if nome == 'DIJKSTRA' else 'V*E+V+E')
            fator = (v+e if nome in ('BFS', 'DFS') else
                     v+e+e*log2(e+1) if nome == 'DIJKSTRA' else v*e+v+e)
            tempo = item['tempo_medio_segundos']
            if referencia_tempo is None:
                referencia_tempo, referencia_fator = tempo, fator
            linhas.append({'algoritmo': nome, 'vertices': v, 'arestas': e,
                           'repeticoes': item['repeticoes'], 'tempo_medio_segundos': tempo,
                           'desvio_padrao_segundos': stdev(item['tempos_segundos']),
                           'formula_referencia': formula, 'fator_referencia': fator,
                           'tempo_relativo': tempo/referencia_tempo if referencia_tempo else None,
                           'fator_relativo': fator/referencia_fator,
                           'segundos_por_fator': tempo/fator})
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open('w', encoding='utf-8', newline='') as arquivo_csv:
        escritor = csv.DictWriter(arquivo_csv, fieldnames=list(linhas[0]))
        escritor.writeheader()
        escritor.writerows(linhas)
    return destino


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--arquivo', default='out/parte2/escalabilidade_report.json')
    parser.add_argument('--out', default='out/parte2/comparacao_complexidades.csv')
    args = parser.parse_args()
    try:
        print(gerar_tabela(args.arquivo, args.out))
    except (ValueError, OSError) as erro:
        parser.exit(1, f'Erro: {erro}\n')


if __name__ == '__main__':
    main()
