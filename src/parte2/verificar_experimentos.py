"""[IA] Codex – verificação dos tempos exportados, sem refazer medições."""
import argparse
from collections import Counter
import json
from math import isclose, isfinite
from pathlib import Path

from .experimentos import ALGORITMOS


def verificar_relatorio(dados):
    """Confere estrutura, repetições, unidade, tempos e média de cada tarefa."""
    erros = []
    experimentos = dados.get('experimentos') if isinstance(dados, dict) else None
    if not isinstance(experimentos, list) or not experimentos:
        return {'valido': False, 'experimentos': 0, 'erros': ['Lista de experimentos vazia ou inválida.']}
    if dados.get('demonstracao') is not False:
        erros.append('O relatório não está identificado como experimento real.')
    for indice, item in enumerate(experimentos):
        prefixo = f'Experimento {indice + 1}: '
        if not isinstance(item, dict):
            erros.append(prefixo + 'registro inválido.')
            continue
        if item.get('algoritmo') not in ALGORITMOS:
            erros.append(prefixo + 'algoritmo desconhecido.')
        for campo, minimo in [('vertices', 1), ('arestas', 0), ('repeticoes', 5)]:
            valor = item.get(campo)
            if type(valor) is not int or valor < minimo:
                erros.append(prefixo + f'{campo} inválido.')
        if item.get('unidade') != 'segundos':
            erros.append(prefixo + 'unidade deve ser segundos.')
        tempos = item.get('tempos_segundos')
        if not isinstance(tempos, list) or not tempos:
            erros.append(prefixo + 'lista de tempos inválida.')
            continue
        if len(tempos) != item.get('repeticoes'):
            erros.append(prefixo + 'quantidade de tempos difere das repetições.')
        if any(type(t) not in (int, float) or not isfinite(t) or t < 0 for t in tempos):
            erros.append(prefixo + 'tempos devem ser finitos e não negativos.')
            continue
        media = item.get('tempo_medio_segundos')
        if (type(media) not in (int, float) or not isfinite(media) or media < 0
                or not isclose(media, sum(tempos) / len(tempos), rel_tol=1e-9, abs_tol=1e-12)):
            erros.append(prefixo + 'média incompatível com os tempos individuais.')
        status = item.get('status_execucoes')
        if (not isinstance(status, list) or len(status) != len(tempos)
                or any(s not in ('OK', 'CICLO_NEGATIVO') for s in status)):
            erros.append(prefixo + 'status das execuções inválido.')
    return {'valido': not erros, 'experimentos': len(experimentos), 'erros': erros}


def verificar_pasta(pasta='out/parte2'):
    """Compara o consolidado com as origens, incluindo escalabilidade se existir."""
    pasta = Path(pasta)
    nomes = ['bfs_dfs_report.json', 'dijkstra_report.json', 'bellman_ford_report.json',
             'parte2_report.json']
    if (pasta / 'escalabilidade_report.json').exists():
        nomes.insert(-1, 'escalabilidade_report.json')
    resultados, carregados = {}, {}
    for nome in nomes:
        try:
            dados = json.loads((pasta / nome).read_text(encoding='utf-8-sig'))
            resultados[nome] = verificar_relatorio(dados)
            if nome == 'escalabilidade_report.json' and resultados[nome]['valido']:
                # Importação local: o módulo de gráficos reutiliza verificar_relatorio.
                from .graficos_escalabilidade import preparar_escalabilidade
                preparar_escalabilidade(dados)
            carregados[nome] = dados
        except (OSError, ValueError) as erro:
            resultados[nome] = {'valido': False, 'experimentos': 0, 'erros': [str(erro)]}
    consistente = False
    if all(resultados[n]['valido'] for n in nomes):
        def assinatura(item):
            return json.dumps(item, sort_keys=True, ensure_ascii=False, allow_nan=False)
        originais = Counter(assinatura(e) for n in nomes[:-1]
                            for e in carregados[n]['experimentos'])
        consolidado = Counter(assinatura(e) for e in carregados[nomes[-1]]['experimentos'])
        consistente = originais == consolidado
    return {'medicoes_validas': all(r['valido'] for r in resultados.values()),
            'consolidado_consistente': consistente, 'arquivos': resultados}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pasta', default='out/parte2')
    parser.add_argument('--out', default='out/parte2/verificacao_experimentos.json')
    args = parser.parse_args()
    destino = Path(args.out)
    # Não permite que a verificação sobrescreva os relatórios examinados.
    protegidos = {(Path(args.pasta) / n).resolve() for n in
                  ['bfs_dfs_report.json', 'dijkstra_report.json',
                   'bellman_ford_report.json', 'escalabilidade_report.json',
                   'parte2_report.json']}
    if destino.resolve() in protegidos:
        parser.error('A saída deve ser diferente dos relatórios de entrada.')
    resultado = verificar_pasta(args.pasta)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    if not resultado['medicoes_validas'] or not resultado['consolidado_consistente']:
        parser.exit(1)


if __name__ == '__main__':
    main()
