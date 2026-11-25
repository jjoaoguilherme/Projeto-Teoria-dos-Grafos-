"""[IA] ChatGPT – utilizado como apoio no entendimento do escopo do data set e possiveis caminhos a se tomar no desenho amostral, papéis das origens e estimadores.

Não implementa algoritmos de grafos nem interpreta resultados acadêmicos.
"""
import math
import random
from statistics import NormalDist, variance

ESTRATOS = ('grau_0', 'grau_1', 'grau_2_10', 'grau_11_100', 'grau_acima_100')


def estrato(grau):
    if not math.isfinite(grau) or grau < 0 or int(grau) != grau:
        raise ValueError('Grau deve ser inteiro não negativo.')
    if grau == 0: return ESTRATOS[0]
    if grau == 1: return ESTRATOS[1]
    if grau <= 10: return ESTRATOS[2]
    if grau <= 100: return ESTRATOS[3]
    return ESTRATOS[4]


def limite_variancia(Nh, nh):
    """Limite da variância da média SRSWOR para uma variável em [0,1]."""
    if Nh <= 1 or nh == Nh: return 0.0
    if not 1 <= nh <= Nh: raise ValueError('Amostra inválida.')
    return .25 * (Nh - nh) / (nh * (Nh - 1))


def planejar(metricas, semente=42, erro_global=.05, erro_estrato=.10, confianca=.95):
    if type(semente) is not int: raise ValueError('Semente deve ser inteira.')
    if not (0 < erro_global < 1 and 0 < erro_estrato < 1 and 0 < confianca < 1):
        raise ValueError('Precisões e confiança devem estar entre zero e um.')
    if metricas.empty or not metricas.index.is_unique:
        raise ValueError('Cadastro deve ser não vazio e ter comunidades únicas.')
    grupos = {h: [] for h in ESTRATOS}
    for origem, grau in metricas.vizinhos_saida.items(): grupos[estrato(grau)].append(origem)
    grupos = {h: sorted(v) for h, v in grupos.items()}
    N = len(metricas); z = NormalDist().inv_cdf((1 + confianca)/2)
    alocacao = {}
    for h, valores in grupos.items():
        Nh = len(valores)
        alocacao[h] = (0 if h == 'grau_0' or not Nh else min(Nh, max(2, math.ceil(
            Nh*z*z*.25 / ((Nh-1)*erro_estrato**2+z*z*.25)))))
    def componente(h, n):
        Nh = len(grupos[h])
        return (Nh/N)**2 * limite_variancia(Nh, n) if Nh and h != 'grau_0' else 0.
    while z*math.sqrt(sum(componente(h, alocacao[h]) for h in ESTRATOS)) > erro_global:
        elegiveis = [h for h in ESTRATOS[1:] if alocacao[h] < len(grupos[h])]
        if not elegiveis: break
        h = max(elegiveis, key=lambda h: componente(h, alocacao[h])-componente(h, alocacao[h]+1))
        alocacao[h] += 1
    registros, estratos = [], []
    # Sementes por estrato tornam a seleção independente da ordem da tabela.
    for i, h in enumerate(ESTRATOS):
        Nh, nh = len(grupos[h]), alocacao[h]
        sorteadas = sorted(random.Random(semente+i*104729).sample(grupos[h], nh))
        estratos.append({'estrato': h, 'N_h': Nh, 'n_h': nh,
                         'censo_estrutural': h == 'grau_0',
                         'avaliados_exatamente_sem_bfs': Nh if h == 'grau_0' else 0,
                         'probabilidade_inclusao_amostra': nh/Nh if Nh else None,
                         'margem_planejada_normal': z*math.sqrt(limite_variancia(Nh,nh)) if nh else 0.})
        for origem in sorteadas:
            registros.append({'origem': origem, 'estrato': h, 'N_h': Nh, 'n_h': nh,
                              'probabilidade_inclusao': nh/Nh, 'peso_amostral': Nh/nh,
                              'peso_media_global': Nh/(N*nh), 'tipo_selecao': 'amostra_analitica'})
    bound = sum(componente(h, alocacao[h]) for h in ESTRATOS)
    return {'versao': 2, 'metodo': 'SRS sem reposição em cada estrato; grau zero conhecido exatamente',
            'semente': semente, 'N': N, 'erro_global_planejado': erro_global,
            'erro_estrato_planejado': erro_estrato, 'confianca_referencia_normal': confianca,
            'z': z, 'limite_variancia_media_global': bound,
            'margem_global_planejada_normal': z*math.sqrt(bound),
            'estratos': estratos, 'amostra': registros, 'n_amostra': len(registros),
            'inclusao': 'Todas as comunidades do arquivo, inclusive apenas destinatárias; nenhuma seleção temporal.',
            'quantis_grau_saida': {str(q): float(metricas.vizinhos_saida.quantile(q)) for q in [.25,.5,.75,.9,.95,.99]},
            'limitacoes': [
                'Alocação desproporcional: médias não ponderadas não estimam a média global.',
                'Metas normais de planejamento não garantem cobertura nem precisão de correlações/distâncias.',
                'Semente, limites e alocação definidos sem usar os resultados de alcance.',
                'Sem inferência para o Reddit além do arquivo; o grafo é tratado como população finita fixa.',
                'Grau zero é censo estrutural separado, não amostra fictícia de buscas executadas.',
                'Não são produzidas correlações amostrais com pretensão de inferência populacional.']}


def registrar_papeis(plano, metricas, obrigatorias, pares):
    amostra = {r['origem']: r for r in plano['amostra']}
    papeis = {}
    for origem in amostra: papeis[origem] = ['amostra_analitica']
    for origem in dict.fromkeys(obrigatorias): papeis.setdefault(origem, []).append('bfs_dfs_obrigatoria')
    for origem in dict.fromkeys(u for u, _ in pares): papeis.setdefault(origem, []).append('par_dijkstra')
    desconhecidas = set(papeis) - set(metricas.index)
    if desconhecidas: raise ValueError('Origens ausentes: '+', '.join(sorted(desconhecidas)))
    if any(v not in metricas.index for _,v in pares): raise ValueError('Destino de Dijkstra ausente.')
    return [{'origem': u, 'finalidades': sorted(set(papeis[u])),
             'amostra_analitica': u in amostra,
             'estrato': estrato(metricas.loc[u,'vizinhos_saida']),
             'probabilidade_inclusao': amostra[u]['probabilidade_inclusao'] if u in amostra else None,
             'peso_amostral': amostra[u]['peso_amostral'] if u in amostra else None}
            for u in sorted(papeis)]


def resumir_bfs(resultado, total_vertices):
    if total_vertices < 1: raise ValueError('Grafo vazio.')
    origem = resultado['inicio']
    if len(resultado['distancias']) != total_vertices or resultado['distancias'].get(origem) != 0:
        raise ValueError('Retorno de BFS incompatível com o grafo.')
    outras = [d for v,d in resultado['distancias'].items() if v != origem and math.isfinite(d)]
    return {'alcance_total': len(outras), 'alcancaveis_incluindo_origem': len(outras)+1,
            'proporcao_alcance': len(outras)/(total_vertices-1) if total_vertices>1 else None,
            'distancia_media_bfs': sum(outras)/len(outras) if outras else None,
            'maior_distancia_bfs': max([0]+outras)}


def estimar_media_alcance(plano, linhas):
    """Média da fração de outras comunidades alcançadas, não correlação."""
    esperado = {r['origem']: r for r in plano['amostra']}
    observadas = {r['origem']: r for r in linhas}
    if len(observadas) != len(linhas) or set(observadas) != set(esperado):
        raise ValueError('Estimativa exige exatamente a amostra analítica completa, sem extras.')
    if plano['N'] <= 1:
        return {'definida':False,'motivo':'Fração de outras comunidades indefinida para N=1.'}
    media, var, detalhes = 0., 0., []
    for h in plano['estratos']:
        Nh, nh = h['N_h'], h['n_h']
        if not Nh: continue
        if h['censo_estrutural']:
            detalhes.append({'estrato':h['estrato'],'media':0.,'erro_padrao':0.,'exato':True});continue
        ys = [observadas[u]['proporcao_alcance'] for u,r in esperado.items() if r['estrato']==h['estrato']]
        if len(ys)!=nh or any(y is None or not math.isfinite(y) or not 0<=y<=1 for y in ys):
            raise ValueError('Fração de alcance inválida ou estrato incompleto.')
        mh = sum(ys)/nh
        vh = (1-nh/Nh)*variance(ys)/nh if nh>1 and nh<Nh else 0.
        w = Nh/plano['N'];media += w*mh;var += w*w*vh
        detalhes.append({'estrato':h['estrato'],'media':mh,'erro_padrao':math.sqrt(vh),'exato':nh==Nh})
    # Chebyshev + limite para variável em [0,1]: cobertura conservadora de desenho,
    # sem depender de normalidade nem de variância observada nula.
    alfa = 1-plano['confianca_referencia_normal']
    margem = math.sqrt(plano['limite_variancia_media_global']/alfa)
    return {'definida':True,'estimando':'Média, por comunidade, da proporção de outras comunidades alcançáveis',
            'media_ponderada':media,'erro_padrao_desenho_estimado':math.sqrt(var),
            'intervalo_conservador_chebyshev':[max(0.,media-margem),min(1.,media+margem)],
            'cobertura_minima_desenho':1-alfa,'margem_conservadora':margem,
            'formula':'soma_h (N_h/N)*media_h; grau zero contribui exatamente 0',
            'estratos':detalhes,
            'aviso':'O erro padrão estimado pode ser zero em amostras homogêneas; não prova ausência de variabilidade populacional.'}
