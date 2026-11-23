"""Amostras aninhadas por vértices para experimentos de escalabilidade.

[IA] Codex – implementação de amostragem reproduzível e metadados.
"""
from math import ceil, isfinite
from random import Random

from src.graphs.graph import Grafo


def criar_amostras(grafo, proporcoes=(0.1, 0.5, 1.0), semente=42,
                   obrigatorios=()):
    """Retorna lista de {grafo, metadados}, ordenada pela proporção.

    Embaralha uma vez a lista de vértices em sua ordem de inserção e usa
    prefixos: a amostra menor está contida na maior. Constrói subgrafos
    induzidos, mantendo ordem original de vértices/arcos, pesos e paralelos.
    A reprodução exige o mesmo grafo, ordem de entrada, parâmetros e runtime.
    Origens/destinos obrigatórios entram em todas as amostras, condicionando
    a seleção; se não couberem na menor, o pedido é rejeitado.
    Não garante conectividade, alcançabilidade ou preservação de ciclos.
    """
    if isinstance(semente, bool) or not isinstance(semente, int):
        raise ValueError('A semente deve ser um inteiro.')
    proporcoes = list(proporcoes)
    if not proporcoes or any(isinstance(p, bool) or not isinstance(p, (int, float))
                            or not isfinite(p) or not 0 < p <= 1 for p in proporcoes):
        raise ValueError('As proporções devem ser números entre 0 e 1, excluindo zero.')
    if len(set(proporcoes)) != len(proporcoes):
        raise ValueError('Não repita proporções.')
    proporcoes.sort()
    vertices, arestas = grafo.vertices, grafo.arestas
    if not vertices:
        raise ValueError('O grafo não pode estar vazio.')
    tamanhos = [ceil(len(vertices) * p) for p in proporcoes]
    if len(set(tamanhos)) != len(tamanhos):
        raise ValueError('As proporções geram tamanhos iguais; use outro grafo ou proporções.')
    fixos = set(obrigatorios)
    if not fixos.issubset(set(vertices)):
        raise ValueError('Vértice obrigatório ausente do grafo.')
    if len(fixos) > min(tamanhos):
        raise ValueError('Os vértices obrigatórios não cabem na menor amostra.')
    candidatos = [v for v in vertices if v not in fixos]
    Random(semente).shuffle(candidatos)
    amostras = []
    for proporcao, tamanho in zip(proporcoes, tamanhos):
        selecionados = fixos | set(candidatos[:tamanho - len(fixos)])
        amostra = Grafo([v for v in vertices if v in selecionados],
                        [(u, v, p) for u, v, p in arestas
                         if u in selecionados and v in selecionados])
        amostras.append({'grafo': amostra, 'metadados': {
            'metodo': 'subgrafo induzido por prefixos de permutação de vértices',
            'semente': semente, 'proporcao_solicitada': proporcao,
            'arredondamento': 'teto', 'amostras_aninhadas': True,
            'vertices_originais': len(vertices), 'arestas_originais': len(arestas),
            'vertices': tamanho, 'arestas': len(amostra.arestas),
            'proporcao_vertices_real': tamanho / len(vertices),
            'proporcao_arestas_real': len(amostra.arestas) / len(arestas) if arestas else None,
            'vertices_selecionados': amostra.vertices,
            'vertices_obrigatorios': [v for v in vertices if v in fixos],
        }})
    return amostras
