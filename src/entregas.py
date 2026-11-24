"""Organiza as saídas existentes das duas partes em páginas de consulta."""
from pathlib import Path
from urllib.parse import quote
import csv
import json
import os


def _renderizar_pagina(nome_modelo, dados, raiz):
    modelos = raiz / 'src/templates'
    pagina = (modelos / nome_modelo).read_text(encoding='utf-8')
    pagina = pagina.replace('/* ESTILOS_ENTREGA */', (modelos / 'entregas.css').read_text(encoding='utf-8'))
    pagina = pagina.replace('/* CODIGO_COMPARTILHADO */', (modelos / 'entregas_comum.js').read_text(encoding='utf-8'))
    serializado = json.dumps(dados, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
    serializado = serializado.replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')
    return pagina.replace('<!-- DADOS_ENTREGA -->', serializado)


def gerar_painel_entregas(pasta='out/parte1', raiz=None):
    """Empacota tabelas exportadas, sem executar algoritmos ou recalcular métricas."""
    raiz = Path(raiz) if raiz else Path(__file__).resolve().parents[1]
    pasta = Path(pasta).resolve()

    def ler_json(nome, padrao=None):
        arquivo = pasta / nome
        return json.loads(arquivo.read_text(encoding='utf-8')) if arquivo.exists() else padrao

    def ler_csv(nome):
        arquivo = pasta / nome
        if not arquivo.exists():
            return []
        with arquivo.open(encoding='utf-8-sig', newline='') as stream:
            return list(csv.DictReader(stream))

    def link(arquivo, titulo=None):
        arquivo = Path(arquivo)
        if not arquivo.is_file():
            return None
        relativo = Path(os.path.relpath(arquivo, pasta)).as_posix()
        return {'nome': titulo or arquivo.name, 'href': quote(relativo, safe='/')}

    metricas = ler_json('metricas_global.json')
    camadas = ler_json('camadas.json')
    if not isinstance(metricas, dict) or not isinstance(camadas, dict):
        raise ValueError('Gere metricas_global.json e camadas.json antes do painel.')
    mapas = {}
    for chave, metrica in sorted(metricas.items()):
        nome = metrica['mapa']
        arquivo_dfs = f'resultado_{nome}_dfs.json'
        dfs = None if metrica['fonte_consumivel'] else ler_json(arquivo_dfs)
        arquivo_mapa = next((p for pasta_mapas in ['mapas', 'mapas_grupo']
                             if (p := raiz / 'data' / pasta_mapas / f'{nome}.txt').is_file()), None)
        arquivos = [link(pasta / f'graus_{chave}.csv'),
                    link(pasta / f'arestas_{chave}.csv')]
        if dfs:
            arquivos.append(link(pasta / arquivo_dfs))
        if arquivo_mapa:
            arquivos.append(link(arquivo_mapa))
        mapas[chave] = {
            'nome': nome,
            'fonte_consumivel': metrica['fonte_consumivel'],
            'rankings': metrica.get('rankings', {}),
            'becos': metrica.get('becos', {}),
            'multiplicidade': metrica.get('multiplicidade', {}),
            'camadas': camadas.get(chave),
            'graus': ler_csv(f'graus_{chave}.csv'),
            'arestas': ler_csv(f'arestas_{chave}.csv'),
            'dfs': ({'tem_ciclo': dfs['tem_ciclo'],
                     'classificacao': dfs['classificacao_arestas']} if dfs else None),
            'arquivos': [a for a in arquivos if a],
        }

    figuras = [
        ('percurso_m03.png', 'Percurso do m03', 'Caminho de menor custo com cor por conjunto de chaves.'),
        ('percurso_m08.png', 'Percurso do m08', 'Caminho de menor custo no mapa grande, com cor por conjunto de chaves.'),
        ('camadas_m02.png', 'Grafo de estados do m02', 'Camadas por conjunto de chaves e arcos que mudam de camada.'),
        ('arvore_bfs_m02.png', 'Árvore BFS do m02', 'Estados organizados pelos níveis da busca em largura.'),
        ('heatmap_m08.png', 'Mapa de calor do m08', 'Multiplicidade: quantidade de estados em cada casa.'),
    ]
    grupos_arquivos = {
        'Métricas e estrutura': ['metricas_global.json', 'camadas.json'],
        'Buscas e análises': ['solucoes.csv', 'dfs_classificacao.csv', 'comparacao_modelagem.csv',
                             'comparacao_bonus_m05.json', 'percurso_m03.json', 'ciclo_negativo_m06.json',
                             'armadilhas_m04.csv', 'armadilhas_m07.csv', 'resumo_mapas.json'],
    }
    documentos = [link(raiz / 'docs/manual_tecnico_parte1.pdf', 'Manual técnico · PDF'),
                  link(raiz / 'docs/CONTRIBUICOES.md', 'Matriz de contribuição · documento'),
                  link(raiz / 'README.md', 'Instruções de execução · README')]
    dados = {
        'mapas': mapas,
        'figuras': [{**a, 'titulo': titulo, 'descricao': descricao}
                    for nome, titulo, descricao in figuras if (a := link(pasta / nome))],
        'modelagens': ler_csv('comparacao_modelagem.csv'),
        'dfs_resumo': ler_csv('dfs_classificacao.csv'),
        'bonus': ler_json('comparacao_bonus_m05.json'),
        'ciclo': ler_json('ciclo_negativo_m06.json'),
        'arquivos': {grupo: [a for nome in nomes if (a := link(pasta / nome))]
                     for grupo, nomes in grupos_arquivos.items()},
        'documentos': [a for a in documentos if a],
        'labirinto': link(pasta / 'labirinto_interativo.html'),
        'parte2': quote(Path(os.path.relpath(pasta.parent / 'parte2/entregas_parte2.html', pasta)).as_posix(), safe='/'),
    }
    pagina = _renderizar_pagina('entregas_parte1.html', dados, raiz)
    destino = pasta / 'entregas_parte1.html'
    destino.write_text(pagina, encoding='utf-8')
    return destino


def gerar_painel_parte2(pasta='out/parte2', raiz=None, pasta_parte1=None):
    """Apresenta os relatórios existentes, preservando valores e sessões de origem."""
    import ast

    raiz = Path(raiz) if raiz else Path(__file__).resolve().parents[1]
    pasta = Path(pasta).resolve()
    pasta.mkdir(parents=True, exist_ok=True)
    pasta_parte1 = Path(pasta_parte1).resolve() if pasta_parte1 else raiz / 'out/parte1'
    relatorios = []
    nomes = ['parte2_report.json', 'bfs_dfs_report.json',
             'dijkstra_report.json', 'bellman_ford_report.json']
    for nome in nomes:
        arquivo = pasta / nome
        if not arquivo.is_file():
            continue
        dados = json.loads(arquivo.read_text(encoding='utf-8'))
        if not isinstance(dados, dict) or not isinstance(dados.get('experimentos'), list):
            raise ValueError(f'{nome} precisa conter uma lista de experimentos.')
        relatorios.append({'nome': nome, 'href': quote(nome), 'dados': dados})

    transformacao = None
    codigo = raiz / 'src/parte2/experimentos.py'
    if codigo.is_file():
        arvore = ast.parse(codigo.read_text(encoding='utf-8-sig'))
        for funcao in arvore.body:
            if isinstance(funcao, ast.FunctionDef) and funcao.name == 'executar_dijkstra':
                for node in ast.walk(funcao):
                    if (isinstance(node, ast.BinOp) and isinstance(node.op, ast.Sub)
                            and isinstance(node.left, ast.Constant) and node.left.value == 2
                            and isinstance(node.right, ast.Name) and node.right.id == 'peso'):
                        transformacao = {'expressao': '2 − peso', 'positivo': 1, 'negativo': 3}

    def rota(arquivo):
        return quote(Path(os.path.relpath(arquivo, pasta)).as_posix(), safe='/')

    resumo = pasta / 'resumo_dataset.json'
    preparacao = json.loads(resumo.read_text(encoding='utf-8')) if resumo.is_file() else None
    candidatos = [
        (resumo, 'Resumo e qualidade · JSON'),
        (pasta / 'arestas_dataset.csv', 'Arcos do grafo · CSV'),
        (pasta / 'base_avd.csv', 'Base de metadados para AVD · CSV'),
        (pasta / 'registros_invalidos.json', 'Registros inválidos · JSON'),
        (raiz / 'data/dataset_parte2/origem_dataset.json', 'Fonte e identificação · JSON'),
        (raiz / 'data/dataset_parte2/soc-redditHyperlinks-title.tsv', 'TSV original completo · download'),
        (raiz / 'docs/preparacao_dataset_parte2.pdf', 'Relatório da preparação · PDF'),
    ]
    arquivos_preparacao = [{'nome': nome, 'href': rota(arquivo)}
                           for arquivo, nome in candidatos if arquivo.is_file()]

    dados = {
        'relatorios': relatorios,
        'preparacao': preparacao,
        'arquivos_preparacao': arquivos_preparacao,
        'parte1': rota(pasta_parte1 / 'entregas_parte1.html'),
        'labirinto': rota(pasta_parte1 / 'labirinto_interativo.html'),
        'dataset_disponivel': any((raiz / 'data/dataset_parte2').glob('*.tsv')),
        'transformacao_dijkstra': transformacao,
        'codigo_experimentos': rota(codigo),
    }
    destino = pasta / 'entregas_parte2.html'
    destino.write_text(_renderizar_pagina('entregas_parte2.html', dados, raiz), encoding='utf-8')
    return destino


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', default='out/parte1', help='Pasta com as saídas existentes da Parte 1.')
    parser.add_argument('--parte', choices=['1', '2', 'todas'], default='todas')
    parser.add_argument('--out-parte2', default='out/parte2', help='Pasta dos relatórios da Parte 2.')
    args = parser.parse_args()
    if args.parte in ('1', 'todas'):
        print(gerar_painel_entregas(args.out))
    if args.parte in ('2', 'todas'):
        print(gerar_painel_parte2(args.out_parte2, pasta_parte1=args.out))
