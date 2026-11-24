"""[IA] Codex – executor configurável de escalabilidade; não escolhe a escala final."""
import argparse
import csv
from hashlib import sha256
from pathlib import Path
from random import Random

from src.graphs.graph import Grafo
from .amostragem import criar_amostras
from .experimentos import medir_algoritmo, registrar_ambiente, exportar_relatorio


def carregar_arestas_preparadas(caminho):
    """Reutiliza o CSV exportado pelo leitor do dataset, preservando seus arcos."""
    grafo = Grafo()
    with Path(caminho).open(encoding='utf-8-sig', newline='') as arquivo:
        leitor = csv.DictReader(arquivo)
        if leitor.fieldnames != ['origem', 'destino', 'peso']:
            raise ValueError('CSV deve ter cabeçalho origem,destino,peso.')
        for numero, linha in enumerate(leitor, 2):
            if None in linha or not linha['origem'] or not linha['destino']:
                raise ValueError(f'Linha {numero}: origem/destino inválidos.')
            try:
                peso = int(linha['peso'])
            except (ValueError, TypeError) as erro:
                raise ValueError(f'Linha {numero}: sentimento inválido.') from erro
            if peso not in (-1, 1):
                raise ValueError(f'Linha {numero}: esperado sentimento -1 ou 1.')
            grafo.adicionar_arco(linha['origem'], linha['destino'], peso)
    return grafo


def medir_escalabilidade(grafo, origem, proporcoes, repeticoes=5, semente=42,
                         limite_vertices=None, identificacao=None):
    """Mede quatro algoritmos nas mesmas amostras, sem cronometrar preparação.

    Proporções são obrigatórias, distintas e pelo menos três. Um limite
    opcional define explicitamente um recorte-base; as porcentagens passam
    a referir-se a esse recorte, e não ao dataset inteiro. Dijkstra usa a
    transformação 2-peso já adotada pelo grupo para sentimentos -1/+1.
    """
    proporcoes = tuple(proporcoes)
    if len(proporcoes) < 3:
        raise ValueError('Informe pelo menos três proporções.')
    if type(repeticoes) is not int or repeticoes < 5:
        raise ValueError('Use pelo menos cinco repetições.')
    vertices_originais = len(grafo.vertices)
    arestas_originais = len(grafo.arestas)
    if any(p not in (-1, 1) for _, _, p in grafo.arestas):
        raise ValueError('Este executor requer sentimentos -1 ou 1.')
    if limite_vertices is not None:
        if type(limite_vertices) is not int or not 3 <= limite_vertices <= vertices_originais:
            raise ValueError('Limite deve estar entre 3 e a ordem do grafo.')
        if origem not in grafo.vertices:
            raise ValueError('Origem ausente do grafo.')
        candidatos = [v for v in grafo.vertices if v != origem]
        Random(semente).shuffle(candidatos)
        selecionados = {origem, *candidatos[:limite_vertices-1]}
        grafo = Grafo([v for v in grafo.vertices if v in selecionados],
                      [(u, v, p) for u, v, p in grafo.arestas
                       if u in selecionados and v in selecionados])
    amostras = criar_amostras(grafo, proporcoes, semente, [origem])
    experimentos = []
    for item in amostras:
        amostra, metadados = item['grafo'], item['metadados']
        vertices, arestas = amostra.vertices, amostra.arestas
        for nome in ('BFS', 'DFS', 'DIJKSTRA', 'BELLMAN_FORD'):
            entrada = [(u, v, 2-p) for u, v, p in arestas] if nome == 'DIJKSTRA' else arestas
            identificador = dict(identificacao or {})
            identificador.update({
                'caso': 'ESCALABILIDADE', 'amostragem': metadados,
                'dataset_vertices': vertices_originais, 'dataset_arestas': arestas_originais,
                'limite_vertices': limite_vertices,
                'pesos': '2 - LINK_SENTIMENT' if nome == 'DIJKSTRA' else 'LINK_SENTIMENT original',
            })
            print(f'{nome}: {len(vertices)} vértices, {len(arestas)} arcos', flush=True)
            experimentos.append(medir_algoritmo(nome, vertices, entrada, origem,
                                                repeticoes, identificacao=identificador))
    return experimentos


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--arquivo', default='out/parte2/arestas_dataset.csv')
    parser.add_argument('--origem', required=True)
    parser.add_argument('--proporcoes', type=float, nargs='+', required=True)
    parser.add_argument('--limite-vertices', type=int)
    parser.add_argument('--semente', type=int, default=42)
    parser.add_argument('--repeticoes', type=int, default=5)
    parser.add_argument('--out', default='out/parte2/escalabilidade_report.json')
    args = parser.parse_args()
    try:
        caminho = Path(args.arquivo)
        grafo = carregar_arestas_preparadas(caminho)
        with caminho.open('rb') as arquivo:
            assinatura = sha256()
            for bloco in iter(lambda: arquivo.read(1024 * 1024), b''):
                assinatura.update(bloco)
        ambiente = registrar_ambiente()
        experimentos = medir_escalabilidade(
            grafo, args.origem, args.proporcoes, args.repeticoes, args.semente,
            args.limite_vertices, {'arquivo': str(caminho), 'sha256': assinatura.hexdigest()})
        destino = exportar_relatorio(experimentos, args.out, ambiente)
    except (ValueError, OSError, csv.Error) as erro:
        parser.exit(1, f'Erro: {erro}\n')
    print(f'Relatório salvo em {destino}')


if __name__ == '__main__':
    main()
