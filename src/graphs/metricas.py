"""Métricas globais de grafos dirigidos e dos labirintos."""
from pathlib import Path
import json

from .estados import construir_grafo_estados, construir_grafo_posicoes
from .io import ler_mapa


def calcular_metricas_grafo(grafo, excluir=()):
    """Conta nós e arcos do subgrafo induzido após excluir os nós indicados."""
    vertices = set(grafo.vertices) - set(excluir)
    ordem = len(vertices)
    tamanho = sum(1 for origem, destino, _ in grafo.arestas
                  if origem in vertices and destino in vertices)
    densidade = tamanho / (ordem * (ordem - 1)) if ordem >= 2 else 0.0
    return {'ordem': ordem, 'tamanho': tamanho, 'densidade': densidade}


def calcular_metricas_mapa(caminho, fonte_consumivel=False):
    """Lê o arquivo e calcula as métricas sem executar caminhos mínimos."""
    matriz, inicio, _ = ler_mapa(caminho)
    dados = construir_grafo_estados(matriz, inicio, fonte_consumivel)
    return calcular_metricas_labirinto(matriz, dados, Path(caminho).stem,
                                      fonte_consumivel)


def calcular_metricas_labirinto(matriz, dados_estados, nome_mapa,
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
