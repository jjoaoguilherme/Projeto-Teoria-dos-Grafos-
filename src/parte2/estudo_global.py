"""[IA] ChatGPT –  ajuda no entendimeto das ferramentas de integração, estatísticas e exportação do estudo global e conceitual dessa etapa do projeto.

As buscas são as implementações existentes do grupo em graphs.algorithms.
"""
import argparse
import hashlib
import json
import math
import time
import platform
from src.graphs import algorithms
from src.parte2.amostragem_fontes import planejar, registrar_papeis, resumir_bfs, estimar_media_alcance
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.graphs.algorithms import BFS, DFS, djikstra, reconstruir_caminho

FONTES = ['subredditdrama', 'bestof', 'titlegore']
PARES = [('xboxone', 'battlefield_4'), ('fitnesscirclejerk', 'leangains'),
         ('jleague', 'soccer'), ('bestof', 'confession'), ('subredditdrama', 'nfl')]


def salvar_json(caminho, valor):
    Path(caminho).write_text(json.dumps(valor, ensure_ascii=False, indent=2,
                                      allow_nan=False) + '\n', encoding='utf-8')


def sha(caminho):
    with Path(caminho).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def preparar_tabelas(df):
    if df.empty: raise ValueError('Base vazia.')
    campos = ['linha_arquivo', 'SOURCE_SUBREDDIT', 'TARGET_SUBREDDIT',
              'POST_ID', 'TIMESTAMP', 'LINK_SENTIMENT']
    if any(c not in df for c in campos):
        raise ValueError('Use base_avd.csv com os metadados completos.')
    ausencias = {c: int((df[c].isna() | df[c].astype(str).str.strip().eq('')).sum()) for c in campos}
    if any(ausencias.values()):
        raise ValueError('Há campos ausentes. Nenhum registro foi excluído; revisar a entrada.')
    if not df.LINK_SENTIMENT.isin([-1, 1]).all():
        raise ValueError('Sentimento diferente de -1/+1.')
    if df.linha_arquivo.duplicated().any():
        raise ValueError('linha_arquivo deve identificar unicamente os registros.')
    datas = pd.to_datetime(df.TIMESTAMP, errors='coerce', format='mixed')
    if datas.isna().any():
        raise ValueError('Há datas inválidas; nenhuma exclusão automática foi aplicada.')
    vertices = sorted(set(df.SOURCE_SUBREDDIT) | set(df.TARGET_SUBREDDIT))
    m = pd.DataFrame(index=pd.Index(vertices, name='comunidade'))
    neg = df[df.LINK_SENTIMENT == -1]
    for sufixo, campo, outro in [('saida', 'SOURCE_SUBREDDIT', 'TARGET_SUBREDDIT'),
                                 ('entrada', 'TARGET_SUBREDDIT', 'SOURCE_SUBREDDIT')]:
        m['referencias_' + sufixo] = df.groupby(campo).size().reindex(vertices, fill_value=0)
        m['vizinhos_' + sufixo] = df.groupby(campo)[outro].nunique().reindex(vertices, fill_value=0)
        m['negativas_' + sufixo] = neg.groupby(campo).size().reindex(vertices, fill_value=0)
        m['proporcao_negativas_' + sufixo] = m['negativas_' + sufixo].div(
            m['referencias_' + sufixo].replace(0, float('nan')))
    pares_neg = set(zip(neg.SOURCE_SUBREDDIT, neg.TARGET_SUBREDDIT))
    ciclos = sorted((u, v) for u, v in pares_neg if u < v and (v, u) in pares_neg)
    participacoes = Counter(v for par in ciclos for v in par)
    m['ciclos_negativos_duas_arestas'] = [participacoes[v] for v in vertices]
    m['em_ciclo_negativo_duas_arestas'] = m.ciclos_negativos_duas_arestas.gt(0)
    n = len(vertices)
    pares = df[['SOURCE_SUBREDDIT', 'TARGET_SUBREDDIT']].drop_duplicates()
    pares_sem_lacos = pares[pares.SOURCE_SUBREDDIT != pares.TARGET_SUBREDDIT]
    mensal = pd.DataFrame({'mes': datas.dt.to_period('M').astype(str),
                           'negativa': df.LINK_SENTIMENT.eq(-1).astype(int)})
    mensal = mensal.groupby('mes').agg(referencias=('negativa', 'size'), negativas=('negativa', 'sum'))
    mensal['proporcao_negativas'] = mensal.negativas / mensal.referencias
    mensal['nao_negativas'] = mensal.referencias - mensal.negativas
    anos = datas.dt.year.value_counts().sort_index()
    outliers = []
    for campo in ['referencias_saida', 'referencias_entrada', 'vizinhos_saida', 'vizinhos_entrada']:
        q1, q3 = m[campo].quantile([.25, .75])
        limite = q3 + 1.5 * (q3 - q1)
        m['candidato_iqr_' + campo] = m[campo] > limite
        outliers.append({'variavel': campo, 'q1': q1, 'q3': q3, 'limite_superior': limite,
                         'candidatos': int((m[campo] > limite).sum()),
                         'tratamento': 'Mantidos; alto grau não é automaticamente erro.'})
    resumo = {'vertices': n, 'referencias': len(df), 'pares_distintos': len(pares),
              'referencias_negativas': len(neg), 'proporcao_negativas': len(neg) / len(df),
              'densidade_suporte_simples_sem_lacos': len(pares_sem_lacos) / (n * (n-1)) if n > 1 else None,
              'lacos': int(df.SOURCE_SUBREDDIT.eq(df.TARGET_SUBREDDIT).sum()),
              'repeticoes_pares': len(df) - len(pares),
              'duplicatas_exatas_sem_numero_linha': int(df[campos[1:]].duplicated().sum()),
              'faltantes': ausencias, 'data_minima': str(datas.min()), 'data_maxima': str(datas.max()),
              'registros_por_ano': {str(k): int(v) for k, v in anos.items()},
              'pares_com_ciclo_negativo_duas_arestas': len(ciclos),
              'comunidades_em_ciclo_negativo_duas_arestas': len(participacoes),
              'top_1pct_share_referencias_saida': float(m.referencias_saida.nlargest(math.ceil(.01*n)).sum()/len(df)),
              'cobertura': 'Arquivo inteiro desde o primeiro registro; sem filtro temporal; rede agregada.',
              'ciclos': 'Contagem de pares distintos com -1 em ambas as direções; não enumera ciclos maiores.',
              'properties': '86 atributos textuais não constam do CSV derivado; não foram analisados.',
              'ausencia': 'Sem vazios nas colunas verificadas; mecanismo de ausência fora da coleta é desconhecido.'}
    return m, mensal, pd.DataFrame(ciclos, columns=['comunidade_a', 'comunidade_b']), pd.DataFrame(outliers), resumo


def selecionar_fontes(metricas, semente=42, erro_global=.05, erro_estrato=.10, confianca=.95):
    """Retorna plano probabilístico; não acrescenta origens obrigatórias à amostra."""
    return planejar(metricas, semente, erro_global, erro_estrato, confianca)


def documentar_caminho(resultado, destino, indice, ponderado):
    caminho = reconstruir_caminho(resultado, destino)
    if not caminho:
        return {'caminho': [], 'arestas': [], 'saltos': None, 'negativas': None, 'custo_transformado': None}
    evidencias = []
    for u, v in zip(caminho, caminho[1:]):
        # Testemunha compatível com as distâncias; o algoritmo não retorna ID da publicação.
        candidatos = indice[(u, v)]
        if ponderado:
            exigido = resultado['distancias'][v] - resultado['distancias'][u]
            candidatos = [r for r in candidatos if 2 - r['peso'] == exigido]
        if not candidatos:
            raise ValueError('Caminho sem referência compatível com as distâncias.')
        evidencias.append(candidatos[0])
    return {'caminho': caminho, 'arestas': evidencias, 'saltos': len(evidencias),
            'negativas': sum(r['peso'] == -1 for r in evidencias),
            'custo_transformado': sum(2 - r['peso'] for r in evidencias)}


def atributos_origem(m, origem):
    r=m.loc[origem]
    dados={c:int(r[c]) for c in ('referencias_entrada','referencias_saida','vizinhos_entrada','vizinhos_saida',
                                 'negativas_entrada','negativas_saida','ciclos_negativos_duas_arestas')}
    for c in ('proporcao_negativas_entrada','proporcao_negativas_saida'):
        dados[c]=None if pd.isna(r[c]) else float(r[c])
    # Grau com multiplicidade = quantidade de referências. Vizinhos = suporte simples.
    dados.update(grau_entrada=dados['referencias_entrada'],grau_saida=dados['referencias_saida'])
    return dados


def carregar_globais(base, existentes, destino):
    assinatura=sha(base)
    existentes=Path(existentes) if existentes else None
    nomes=['comunidades.csv','mensal.csv','ciclos_negativos_duas_arestas.csv','outliers_iqr.csv',
           'correlacoes_pearson.csv','correlacoes_spearman.csv','resumo_global.json']
    if existentes and all((existentes/n).is_file() for n in nomes):
        resumo=json.loads((existentes/'resumo_global.json').read_text(encoding='utf8'))
        if resumo.get('sha256_base') != assinatura:
            raise ValueError('As tabelas globais existentes não correspondem ao hash da base. Use --recalcular-globais para gerar uma nova versão.')
        # Nomes como "nan" e "null" podem ser identificadores legítimos.
        m=pd.read_csv(existentes/'comunidades.csv',index_col='comunidade',keep_default_na=False)
        for coluna in ('proporcao_negativas_entrada','proporcao_negativas_saida'):
            m[coluna]=pd.to_numeric(m[coluna].replace('',float('nan')),errors='raise')
        if len(m)!=resumo['vertices'] or not m.index.is_unique:
            raise ValueError('Cadastro global inconsistente.')
        origem=existentes.resolve()
        reutilizadas=True
    else:
        df=pd.read_csv(base,keep_default_na=False)
        m,mensal,ciclos,outliers,resumo=preparar_tabelas(df)
        origem=destino/'globais';origem.mkdir()
        m.to_csv(origem/'comunidades.csv');mensal.to_csv(origem/'mensal.csv')
        ciclos.to_csv(origem/'ciclos_negativos_duas_arestas.csv',index=False)
        outliers.to_csv(origem/'outliers_iqr.csv',index=False)
        numericas=m.select_dtypes(include=['number'])
        numericas.corr().to_csv(origem/'correlacoes_pearson.csv')
        numericas.rank().corr().to_csv(origem/'correlacoes_spearman.csv')
        resumo['sha256_base']=assinatura;salvar_json(origem/'resumo_global.json',resumo)
        reutilizadas=False
    return m, resumo, {'pasta':str(origem),'reutilizadas':reutilizadas,
                       'sha256_base':assinatura,'hashes_artefatos':{n:sha(origem/n) for n in nomes}}


def executar(base='out/parte2/base_avd.csv', out='out/parte2/global_amostragem_v2',
             modo='planejar', globais_existentes='out/parte2/global', semente=42,
             erro_global=.05, erro_estrato=.10, confianca=.95,
             comparar_nao_negativas=False, limite_segundos=900,
             fontes_obrigatorias=None, pares=None):
    """Planeja, faz piloto ou executa com cache. Não refaz benchmarks existentes."""
    if modo not in ('planejar','piloto','executar'):raise ValueError('Modo inválido.')
    if limite_segundos<=0:raise ValueError('Limite de tempo deve ser positivo.')
    obrigatorias=FONTES if fontes_obrigatorias is None else fontes_obrigatorias
    pares=PARES if pares is None else list(dict.fromkeys(pares))
    destino=Path(out);destino.mkdir(parents=True,exist_ok=True)
    # Reutiliza tabelas geradas aqui em uma invocação anterior.
    fonte_globais=destino/'globais' if (destino/'globais/resumo_global.json').exists() else globais_existentes
    m,resumo,proveniencia=carregar_globais(base,fonte_globais,destino)
    plano=selecionar_fontes(m,semente,erro_global,erro_estrato,confianca)
    papeis=registrar_papeis(plano,m,obrigatorias,pares)
    chave={'versao':2,'base':proveniencia['sha256_base'],'algoritmos':sha(algorithms.__file__),
           'executor':sha(__file__),'amostragem':sha(Path(__file__).with_name('amostragem_fontes.py')),
           'plano':plano,'papeis':papeis,'pares':pares,'comparar_nao_negativas':comparar_nao_negativas,
           'metricas':proveniencia['hashes_artefatos']['comunidades.csv']}
    assinatura=hashlib.sha256(json.dumps(chave,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    meta=destino/'execucao.json'
    if meta.exists() and json.loads(meta.read_text(encoding='utf8'))['assinatura']!=assinatura:
        raise ValueError('Dados, código ou parâmetros mudaram; use outra pasta --out. Cache anterior preservado.')
    salvar_json(meta,{'assinatura':assinatura,'configuracao':chave,'python':platform.python_version()})
    salvar_json(destino/'globais_reutilizados.json',proveniencia)
    plano.update(total_origens_distintas_execucao=len(papeis),
                 n_obrigatorias=len(set(obrigatorias)),n_origens_pares=len(set(u for u,v in pares)),
                 comparacao_nao_negativas= comparar_nao_negativas)
    salvar_json(destino/'plano_amostral.json',plano)
    salvar_json(destino/'registro_origens.json',papeis)
    print('Amostra analítica:',plano['n_amostra'],'| Origens distintas:',len(papeis),flush=True)
    if modo=='planejar':return plano
    cache=destino/'cache';cache.mkdir(exist_ok=True)
    def caminho_cache(u):return cache/(hashlib.sha256(u.encode()).hexdigest()+'.json')
    def ler_cache(u):
        p=caminho_cache(u)
        if not p.exists():return None
        item=json.loads(p.read_text(encoding='utf8'))
        if item['assinatura']!=assinatura or item['resultado']['origem']!=u:
            raise ValueError('Cache incompatível.')
        return item
    # Nenhum grafo é reduzido; somente as origens são amostradas.
    df=pd.read_csv(base,keep_default_na=False)
    if len(df)!=resumo['referencias'] or set(df.SOURCE_SUBREDDIT)|set(df.TARGET_SUBREDDIT)!=set(m.index):
        raise ValueError('Cadastro global difere da base.')
    vertices=list(dict.fromkeys(no for par in zip(df.SOURCE_SUBREDDIT,df.TARGET_SUBREDDIT) for no in par))
    arestas=list(zip(df.SOURCE_SUBREDDIT,df.TARGET_SUBREDDIT,df.LINK_SENTIMENT.astype(int)))
    positivas=[a for a in arestas if a[2]==1] if comparar_nao_negativas else None
    transformadas=None;indice=None
    registros={r['origem']:r for r in plano['amostra']}
    roles={r['origem']:r['finalidades'] for r in papeis}
    def calcular(u):
        nonlocal transformadas,indice
        anterior=ler_cache(u)
        if anterior:return anterior
        t=time.perf_counter();bfs=BFS(vertices,arestas,u);tempo_bfs=time.perf_counter()-t
        result={'origem':u,**atributos_origem(m,u),**resumir_bfs(bfs,len(vertices)),
                'finalidades':roles[u], 'amostra_analitica':u in registros,
                'estrato':next(r['estrato'] for r in papeis if r['origem']==u)}
        if u in registros:result.update(registros[u])
        pos_t=0.
        if comparar_nao_negativas and (u in registros or u in obrigatorias):
            t=time.perf_counter();pos=BFS(vertices,positivas,u);pos_t=time.perf_counter()-t
            rp=resumir_bfs(pos,len(vertices))
            if any(math.isfinite(d) and not math.isfinite(bfs['distancias'][v]) for v,d in pos['distancias'].items()):
                raise ValueError('Remoção de arestas aumentou conjunto alcançável.')
            result.update(alcance_so_nao_negativas=rp['alcance_total'],
                          perda_alcance_remocao_negativas=result['alcance_total']-rp['alcance_total'])
        if u in obrigatorias:
            dfs=DFS(vertices,arestas,u)
            if set(dfs['ordem_visita'])!={v for v,d in bfs['distancias'].items() if math.isfinite(d)}:
                raise ValueError('Conjuntos BFS/DFS divergentes.')
            result.update(tem_ciclo_dfs=dfs['tem_ciclo'],
                          classificacao_dfs=dict(Counter(a[2] for a in dfs['classificacao_arestas'])))
        docs=[]
        alvos=[v for origem,v in pares if origem==u]
        if alvos:
            if transformadas is None:transformadas=[(a,b,2-p) for a,b,p in arestas]
            if indice is None:
                indice={}
                for linha in df.itertuples(index=False):
                    opcoes=indice.setdefault((linha.SOURCE_SUBREDDIT,linha.TARGET_SUBREDDIT),[])
                    if not any(r['peso']==linha.LINK_SENTIMENT for r in opcoes):
                        opcoes.append({'peso':int(linha.LINK_SENTIMENT),'linha_tsv':int(linha.linha_arquivo),
                                       'post_id':linha.POST_ID,'timestamp':linha.TIMESTAMP,
                                       'origem':linha.SOURCE_SUBREDDIT,'destino':linha.TARGET_SUBREDDIT})
            d=djikstra(vertices,transformadas,u)
            for v in alvos:
                docs.append({'origem':u,'destino':v,'bfs':documentar_caminho(bfs,v,indice,False),
                             'dijkstra':documentar_caminho(d,v,indice,True),
                             'escopo':'Par predefinido; não compõe estimativa da amostra analítica.'})
        item={'assinatura':assinatura,'resultado':result,'caminhos':docs,
              'tempos_operacionais':{'bfs':tempo_bfs,'bfs_nao_negativas':pos_t}}
        temporario=caminho_cache(u).with_suffix('.tmp');salvar_json(temporario,item);temporario.replace(caminho_cache(u))
        return item
    if modo=='piloto':
        tempos={}
        for h in plano['estratos']:
            origens=[r['origem'] for r in plano['amostra'] if r['estrato']==h['estrato']][:3]
            tempos[h['estrato']]=[]
            for u in origens:
                print('Piloto:',u,flush=True);d=calcular(u)
                tempos[h['estrato']].append(sum(d['tempos_operacionais'].values()))
        total=sum(h['n_h']*max(tempos[h['estrato']],default=0) for h in plano['estratos'])
        custos={'metodo':'máximo observado em até 3 fontes por estrato; fator operacional 1,5',
                'tempos_por_estrato':tempos,'estimativa_bfs_total_segundos':1.5*total,
                'estimativa_restante_conservadora_segundos':1.5*total,
                'inclui':'BFS completa e comparação sem negativas se habilitada; piloto reutilizado no cache.',
                'nao_inclui':'Leitura, exportação e até 3 DFS/5 Dijkstra das origens obrigatórias.',
                'aviso':'Estimativa operacional, não intervalo de confiança nem benchmark.'}
        salvar_json(destino/'piloto_custo.json',custos);print(json.dumps(custos,ensure_ascii=False,indent=2));return custos
    piloto=destino/'piloto_custo.json'
    if not piloto.exists():raise ValueError('Execute --modo piloto antes de --modo executar.')
    custo=json.loads(piloto.read_text(encoding='utf8'))['estimativa_restante_conservadora_segundos']
    if custo>limite_segundos:raise ValueError(f'Estimativa {custo:.1f}s supera limite {limite_segundos}s. A amostra não foi reduzida; ajuste --limite-segundos conscientemente.')
    linhas=[];caminhos=[]
    for i,papel in enumerate(papeis,1):
        u=papel['origem'];d=calcular(u);linhas.append(d['resultado']);caminhos.extend(d['caminhos'])
        print(f'{i}/{len(papeis)} {u}',flush=True)
    analiticas=[r for r in linhas if r['amostra_analitica']]
    # Nenhuma origem técnica é acrescentada ao estimador só por ser obrigatória.
    pd.DataFrame(analiticas).to_csv(destino/'amostra_analitica.csv',index=False)
    pd.DataFrame(analiticas).to_csv(destino/'fontes_resultados.csv',index=False)
    tecnicas=[r for r in linhas if 'bfs_dfs_obrigatoria' in r['finalidades'] or 'par_dijkstra' in r['finalidades']]
    pd.DataFrame(tecnicas).to_csv(destino/'origens_experimentos.csv',index=False)
    zeros=[]
    for u in m.index[m.vizinhos_saida==0]:
        zeros.append({'origem':u,**atributos_origem(m,u),'alcance_total':0,
                      'proporcao_alcance':0 if len(m)>1 else None,'distancia_media_bfs':None,
                      'maior_distancia_bfs':0,'estrato':'grau_0','metodo':'exato_por_ausencia_de_saidas',
                      'probabilidade_cobertura':1,'bfs_executada':False})
    pd.DataFrame(zeros,columns=list(zeros[0]) if zeros else ['origem','alcance_total','metodo']).to_csv(destino/'censo_grau_zero.csv',index=False)
    salvar_json(destino/'estimativa_media_alcance.json',estimar_media_alcance(plano,analiticas))
    salvar_json(destino/'caminhos_documentados.json',caminhos)
    salvar_json(destino/'CONCLUIDO.json',{'versao':2,'concluido':True,'amostra_analitica':len(analiticas),
                'origens_distintas':len(linhas),'comunidades_grau_zero_exatas':len(zeros),
                'pares_documentados':len(caminhos),'assinatura':assinatura,
                'escopo':'Métricas globais exatas separadas de estimativas amostrais. Sem conclusões acadêmicas.',
                'compatibilidade':'Não alimentar os gráficos/textos antigos com premissas fixas de 19 fontes.'})
    return plano


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base',default='out/parte2/base_avd.csv')
    parser.add_argument('--out',default='out/parte2/global_amostragem_v2')
    parser.add_argument('--modo',choices=['planejar','piloto','executar'],default='planejar')
    parser.add_argument('--globais-existentes',default='out/parte2/global')
    parser.add_argument('--recalcular-globais',action='store_true')
    parser.add_argument('--semente',type=int,default=42)
    parser.add_argument('--erro-global',type=float,default=.05)
    parser.add_argument('--erro-estrato',type=float,default=.10)
    parser.add_argument('--confianca',type=float,default=.95)
    parser.add_argument('--comparar-nao-negativas',action='store_true')
    parser.add_argument('--limite-segundos',type=float,default=900)
    args=parser.parse_args()
    executar(args.base,args.out,args.modo,None if args.recalcular_globais else args.globais_existentes,
             args.semente,args.erro_global,args.erro_estrato,args.confianca,args.comparar_nao_negativas,args.limite_segundos)


