"""[IA] Codex – CLI da integração mapa → estados → Bellman-Ford."""
import argparse
import json
from .solve import resolver_mapa, exportar_resultado


def main():
    parser = argparse.ArgumentParser(description='Bellman-Ford em labirintos com estados.')
    parser.add_argument('--mapa', required=True)
    parser.add_argument('--alg', choices=['BELLMAN_FORD'], default='BELLMAN_FORD')
    parser.add_argument('--out', default='out/parte1')
    parser.add_argument('--fonte-consumivel', action='store_true')
    args = parser.parse_args()
    try:
        relatorio, grafo = resolver_mapa(args.mapa, args.fonte_consumivel)
        exportar_resultado(relatorio, grafo, args.out)
    except (OSError, ValueError) as erro:
        parser.exit(1, f'Erro: {erro}\n')
    resumo = {k: relatorio[k] for k in ('mapa', 'status', 'passos', 'custo',
                                      'estados_alcancaveis', 'custo_ciclo', 'ciclo_afeta_alvo')}
    print(json.dumps(resumo, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
