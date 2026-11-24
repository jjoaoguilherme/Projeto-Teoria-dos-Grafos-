"""Geração reproduzível das entregas da Parte 1."""
from pathlib import Path
import csv
import json
from .graphs.analises import estados_armadilha, exportar_armadilhas, comparar_modelagens, comparar_bonus
from .graphs.io import ler_mapa


def gerar_parte1(pasta='out/parte1', mapa_extra=None):
    from .main import resolver_mapa, exportar_resultado
    from .viz import gerar_figuras, atualizar_html
    raiz = Path(__file__).resolve().parents[1]
    pasta = Path(pasta);pasta.mkdir(parents=True, exist_ok=True)
    comparacoes = [];resumos = {};dados_mapas = {}
    mapas = sorted((raiz/'data/mapas').glob('*.txt')) + sorted((raiz/'data/mapas_grupo').glob('*.txt'))
    if mapa_extra and Path(mapa_extra).resolve() not in {p.resolve() for p in mapas}:
        if Path(mapa_extra).stem in {p.stem for p in mapas}:
            raise ValueError('O mapa adicional precisa de nome distinto dos mapas fornecidos.')
        mapas.append(Path(mapa_extra))
    for nome in ['solucoes.csv','dfs_classificacao.csv']:
        (pasta/nome).unlink(missing_ok=True)
    for caminho in mapas:
        matriz, inicio, _ = ler_mapa(caminho)
        resultados = {}
        for alg in ['BFS', 'DFS', 'DIJKSTRA', 'BELLMAN_FORD']:
            r,d = resolver_mapa(caminho, algoritmo=alg)
            exportar_resultado(r,d,pasta);resultados[alg] = r
        armadilhas = estados_armadilha(d)
        if caminho.stem.startswith(('m04','m07')):exportar_armadilhas(d,caminho.stem,pasta)
        resumos[caminho.stem] = {'estados': len(d['estados']),
             'arcos': r['metricas_globais']['G_est']['tamanho'],
             'passos_bfs': resultados['BFS']['passos'], 'custo': r['custo'],
             'armadilhas': len(armadilhas), 'taxa_armadilhas': len(armadilhas)/len(d['estados'])}
        dados_mapas[caminho.stem] = {'matriz': matriz, 'dados': d, 'armadilhas': armadilhas}
        if caminho.stem.startswith(('m02','m03','m04')):comparacoes.extend(comparar_modelagens(matriz,inicio,caminho.stem))
        if caminho.stem.startswith('m05'):
            (pasta/'comparacao_bonus_m05.json').write_text(json.dumps(comparar_bonus(matriz,inicio),ensure_ascii=False,indent=2),encoding='utf-8')
        if caminho.stem.startswith('m06'):
            corrigido,g = resolver_mapa(caminho,True)
            exportar_resultado(corrigido,g,pasta)
    with (pasta/'comparacao_modelagem.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['mapa','abordagem','passos','caminho_valido','observacao']);w.writeheader();w.writerows(comparacoes)
    (pasta/'resumo_mapas.json').write_text(json.dumps(resumos,ensure_ascii=False,indent=2),encoding='utf-8')
    gerar_figuras(pasta,dados_mapas)
    atualizar_html(pasta,dados_mapas,raiz/'out/parte1/labirinto_interativo.html')
    from .relatorio import gerar_relatorio
    gerar_relatorio(pasta, raiz/'docs/manual_tecnico_parte1.pdf')
    from .entregas import gerar_painel_entregas, gerar_painel_parte2
    gerar_painel_entregas(pasta, raiz)
    gerar_painel_parte2(pasta.parent / 'parte2', raiz, pasta)
    return resumos
