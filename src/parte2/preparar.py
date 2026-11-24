"""Obtém, valida e exporta a base do Reddit em um único comando."""
import argparse
import json
from pathlib import Path

from .dados import carregar_dataset, exportar_dataset
from .obter_dataset import DESTINO, obter_dataset


def preparar_dataset(arquivo=DESTINO, pasta='out/parte2'):
    caminho = obter_dataset(arquivo)
    print('Construindo o grafo e conferindo os atributos...', flush=True)
    dados = carregar_dataset(caminho)
    relatorio = dados['relatorio']
    if not relatorio['atinge_20_mil_arestas']:
        raise ValueError('A base preparada precisa ter pelo menos 20 mil arcos válidos.')
    if not relatorio['contagens']['negativos']:
        raise ValueError('Nenhum arco com peso negativo foi encontrado.')
    manifesto = caminho.parent / 'origem_dataset.json'
    relatorio['origem'] = json.loads(manifesto.read_text(encoding='utf-8'))
    print('Exportando resumo, arcos e base para AVD...', flush=True)
    exportar_dataset(dados, pasta)
    from .relatorio_dados import gerar_relatorio_dados
    raiz = Path(__file__).resolve().parents[2]
    gerar_relatorio_dados(relatorio, raiz / 'docs/preparacao_dataset_parte2.pdf')
    from ..entregas import gerar_painel_parte2
    gerar_painel_parte2(pasta, raiz)
    print(f'Base pronta: {relatorio["vertices"]} vértices e {relatorio["arestas"]} arcos.', flush=True)
    print(f'Saídas em {Path(pasta)}; relatório em docs/preparacao_dataset_parte2.pdf.', flush=True)
    return relatorio


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--arquivo', default=str(DESTINO))
    parser.add_argument('--out', default='out/parte2')
    args = parser.parse_args()
    try:
        preparar_dataset(args.arquivo, args.out)
    except (OSError, ValueError) as erro:
        parser.exit(1, f'Erro: {erro}\n')


if __name__ == '__main__':
    main()
