"""Métricas globais de grafos dirigidos e dos labirintos."""
from pathlib import Path
import json
import csv
from collections import Counter

from .estados import construir_grafo_estados, construir_grafo_posicoes
from .io import ler_mapa


def _resumir_metricas(ordem, tamanho):
    densidade = tamanho / (ordem * (ordem - 1)) if ordem >= 2 else 0.0
    return {'ordem': ordem, 'tamanho': tamanho, 'densidade': densidade}


def calcular_metricas_grafo(grafo, excluir=()):
    """Conta nós e arcos do subgrafo induzido após excluir os nós indicados."""
    vertices = set(grafo.vertices) - set(excluir)
    ordem = len(vertices)
    tamanho = sum(1 for origem, destino, _ in grafo.arestas
                  if origem in vertices and destino in vertices)
    return _resumir_metricas(ordem, tamanho)


def calcular_metricas_mapa(caminho, fonte_consumivel=False):
    """Lê o arquivo e calcula as métricas sem executar caminhos mínimos."""
    return calcular_pacote_mapa(caminho, fonte_consumivel)['globais']


def _calcular_metricas_basicas(matriz, dados_estados, nome_mapa,
                               fonte_consumivel=False):
    """Calcula métricas reutilizando os estados já construídos pelo chamador.

    G_pos inclui todas as casas livres com portas como chão. As métricas de
    G_est excluem ALVO e seus arcos. O teto usa tipos distintos de chaves e
    cada consumível individual; fontes só são consumíveis no modo opcional.
    """
    g_pos = construir_grafo_posicoes(matriz, portas='chao')
    m_pos = calcular_metricas_grafo(g_pos)
    casas_livres = m_pos['ordem']
    chaves = sorted({simbolo for linha in matriz for simbolo in linha
                     if simbolo in 'abcd'})
    numero_bonus = sum(simbolo == '+' for linha in matriz for simbolo in linha)
    numero_fontes_consumiveis = (
        sum(simbolo == '*' for linha in matriz for simbolo in linha)
        if fonte_consumivel else 0
    )
    teto = casas_livres * 2 ** (len(chaves) + numero_bonus + numero_fontes_consumiveis)
    m_est = calcular_metricas_grafo(dados_estados['grafo'], excluir={'ALVO'})
    return {
        'mapa': nome_mapa,
        'fonte_consumivel': fonte_consumivel,
        'casas_livres': casas_livres,
        'chaves': chaves,
        'numero_chaves': len(chaves),
        'numero_bonus': numero_bonus,
        'numero_fontes_consumiveis': numero_fontes_consumiveis,
        'G_pos': m_pos,
        'G_est': m_est,
        'teto_teorico': teto,
        'taxa_ocupacao': m_est['ordem'] / teto,
    }



def calcular_metricas_percurso(percurso):
    """Indicadores do percurso completo; sem percurso, valores indisponíveis.

    O custo acumulado já foi calculado ao reconstruir o caminho. Aqui ele é
    apenas lido, sem somar pesos novamente. A fonte não contém o nó ALVO.
    """
    if not percurso:
        return {'passos': None, 'custo': None,
                'custo_medio_por_movimento': None, 'casas_distintas': None}
    passos = len(percurso) - 1
    custo = percurso[-1]['custo_acumulado']
    return {
        'passos': passos,
        'custo': custo,
        'custo_medio_por_movimento': custo / passos if passos else None,
        'casas_distintas': len({tuple(p['posicao']) for p in percurso}),
    }


def exportar_metricas_globais(metricas, pasta):
    """Atualiza os mapas informados sem apagar entradas de outros mapas/modos.

    Cada entrada é identificada pelo nome do arquivo sem extensão. O modo
    fonte consumível recebe sufixo próprio, preservando a execução normal.
    """
    arquivo = Path(pasta) / 'metricas_global.json'
    dados = {}
    if arquivo.exists():
        dados = json.loads(arquivo.read_text(encoding='utf-8'))
        if not isinstance(dados, dict):
            raise ValueError('metricas_global.json deve conter um objeto JSON.')
    for metrica in metricas:
        nome = metrica['mapa']
        if metrica['fonte_consumivel']:
            nome += '_fonte_consumivel'
        dados[nome] = metrica
    texto = json.dumps(dados, ensure_ascii=False, indent=2,
                       sort_keys=True, allow_nan=False) + '\n'
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(texto, encoding='utf-8')
    return arquivo


def calcular_detalhes_estados(matriz, dados_estados):
    """Graus, rankings e subgrafos induzidos, excluindo ALVO e seus arcos.

    Empates de ranking usam ordem lexicográfica dos rótulos completos.
    Bônus diferentes permanecem na mesma camada se as chaves forem iguais.
    """
    estados = dados_estados['estados']
    rotulos = sorted(estados)
    entradas = dict.fromkeys(rotulos, 0)
    saidas = dict.fromkeys(rotulos, 0)
    camada_por_estado = {r: ''.join(sorted(e[1])) or '-' for r, e in estados.items()}
    nos_camadas = Counter(camada_por_estado.values())
    arcos_camadas = Counter()
    transicoes = Counter()
    casas_transicao = Counter()
    for origem, destino, _ in dados_estados['grafo'].arestas:
        if origem not in estados or destino not in estados:
            continue
        saidas[origem] += 1
        entradas[destino] += 1
        a, b = camada_por_estado[origem], camada_por_estado[destino]
        if a == b:
            arcos_camadas[a] += 1
        else:
            transicoes[(a, b)] += 1
            casas_transicao[estados[destino][0]] += 1

    def ranking(graus):
        if not rotulos:
            return None
        vencedor = min(rotulos, key=lambda r: (-graus[r], r))
        return {'estado': vencedor, 'grau': graus[vencedor]}

    becos = [r for r in rotulos if saidas[r] == 0
             and matriz[estados[r][0][0]][estados[r][0][1]] != 'G']
    multiplicidade = Counter(e[0] for e in estados.values())
    maximo = max(multiplicidade.values(), default=0)
    casas_maximas = [list(p) for p, n in sorted(multiplicidade.items()) if n == maximo]
    por_casa = [{'posicao': [i, j], 'multiplicidade': multiplicidade[(i, j)]}
                for i, linha in enumerate(matriz) for j, simbolo in enumerate(linha)
                if simbolo != '#']
    camadas = {}
    for camada, ordem in sorted(nos_camadas.items()):
        tamanho = arcos_camadas[camada]
        camadas[camada] = _resumir_metricas(ordem, tamanho)
    return {
        'graus': [{'estado': r, 'grau_entrada': entradas[r], 'grau_saida': saidas[r]}
                  for r in rotulos],
        'rankings': {'maior_grau_entrada': ranking(entradas),
                     'maior_grau_saida': ranking(saidas)},
        'becos': {'quantidade': len(becos), 'estados': becos},
        'multiplicidade': {'maxima': maximo, 'quantidade_casas_maximas': len(casas_maximas),
                           'casas_maximas': casas_maximas, 'por_casa': por_casa},
        'camadas': {
            'camadas': camadas,
            'arcos_entre_camadas': {
                'quantidade': sum(transicoes.values()),
                'transicoes': [{'origem': a, 'destino': b, 'quantidade': n}
                               for (a, b), n in sorted(transicoes.items())],
                'por_casa': [{'posicao': list(p), 'chave': matriz[p[0]][p[1]], 'quantidade': n}
                             for p, n in sorted(casas_transicao.items())],
            },
        },
    }


def calcular_pacote_metricas(matriz, dados_estados, nome_mapa, fonte_consumivel=False):
    """Reúne as três entregas de métricas reutilizando o grafo já construído."""
    globais = _calcular_metricas_basicas(matriz, dados_estados, nome_mapa, fonte_consumivel)
    detalhes = calcular_detalhes_estados(matriz, dados_estados)
    for campo in ['rankings', 'becos', 'multiplicidade']:
        globais[campo] = detalhes[campo]
    return {'globais': globais, 'graus': detalhes['graus'], 'camadas': detalhes['camadas']}


def calcular_metricas_labirinto(matriz, dados_estados, nome_mapa, fonte_consumivel=False):
    return calcular_pacote_metricas(matriz, dados_estados, nome_mapa, fonte_consumivel)['globais']


def calcular_pacote_mapa(caminho, fonte_consumivel=False):
    matriz, inicio, _ = ler_mapa(caminho)
    dados = construir_grafo_estados(matriz, inicio, fonte_consumivel)
    return calcular_pacote_metricas(matriz, dados, Path(caminho).stem, fonte_consumivel)


def exportar_pacotes_metricas(pacotes, pasta):
    """Atualiza globais, camadas e CSVs de graus; preserva outros mapas/modos."""
    pacotes = list(pacotes)
    pasta = Path(pasta)
    arquivo_camadas = pasta / 'camadas.json'
    camadas = json.loads(arquivo_camadas.read_text(encoding='utf-8')) if arquivo_camadas.exists() else {}
    if not isinstance(camadas, dict):
        raise ValueError('camadas.json deve conter um objeto JSON.')
    for pacote in pacotes:
        m = pacote['globais']
        nome = m['mapa'] + ('_fonte_consumivel' if m['fonte_consumivel'] else '')
        camadas[nome] = pacote['camadas']
    texto = json.dumps(camadas, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + '\n'
    arquivo = exportar_metricas_globais([p['globais'] for p in pacotes], pasta)
    arquivo_camadas.write_text(texto, encoding='utf-8')
    for pacote in pacotes:
        m = pacote['globais']
        nome = m['mapa'] + ('_fonte_consumivel' if m['fonte_consumivel'] else '')
        with (pasta / f'graus_{nome}.csv').open('w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['estado', 'grau_entrada', 'grau_saida'])
            writer.writeheader()
            writer.writerows(pacote['graus'])
    return arquivo
