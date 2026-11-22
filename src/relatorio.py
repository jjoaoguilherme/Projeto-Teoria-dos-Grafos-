"""Manual técnico reproduzível a partir das saídas da Parte 1."""
from pathlib import Path
import json
import csv
from xml.sax.saxutils import escape


def gerar_relatorio(pasta, destino):
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    pasta=Path(pasta);destino=Path(destino);destino.parent.mkdir(parents=True,exist_ok=True)
    estilos=getSampleStyleSheet();story=[]
    estilos['Heading1'].keepWithNext=True
    estilos['Heading2'].keepWithNext=True
    def texto(t,estilo='BodyText'):
        story.append(Paragraph(escape(t),estilos[estilo]));story.append(Spacer(1,9))
    def tabela(rows):
        t=Table(rows,repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.lightgrey),('GRID',(0,0),(-1,-1),.3,colors.grey),('FONTSIZE',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),6)]));story.append(t);story.append(Spacer(1,14))
    def imagem(nome,largura=470):
        im=Image(str(pasta/nome));proporcao=im.imageHeight/im.imageWidth;im.drawWidth=largura;im.drawHeight=largura*proporcao
        if im.drawHeight>590:im.drawHeight=590;im.drawWidth=590/proporcao
        story.append(im)
    resumo=json.loads((pasta/'resumo_mapas.json').read_text(encoding='utf-8'))
    texto('Labirintos com chaves e portas','Title')
    texto('Manual de execução e relatório técnico da Parte 1','Heading2')
    texto('Modelo dirigido de estados, algoritmos próprios e resultados reproduzíveis. Este documento cobre a Parte 1. Identificação dos integrantes, contribuição efetiva e assinaturas devem ser completadas pelo grupo antes da entrega.')
    texto('Instalação e execução','Heading1')
    for t in ['Python 3.11 ou superior. Na raiz: python -m venv .venv; instalar com .venv/Scripts/python -m pip install -r requirements.txt.',
              'Gerar todas as entregas: python -m src.cli --parte1-completa --out out/parte1',
              'Executar mapa: python -m src.cli --mapa data/mapas/m02_uma_chave.txt --alg BFS --out out/parte1',
              'Algoritmos disponíveis: BFS, DFS, DIJKSTRA e BELLMAN_FORD. --fonte-consumivel corrige a fonte repetível; --armadilhas exporta estados sem acesso ao alvo; --interactive gera a interface, incluindo o mapa informado.',
              'Abrir out/parte1/labirinto_interativo.html no navegador. Selecionar mapa, algoritmo e camada; usar avanço manual, reprodução e velocidade. A borda vermelha indica posições com estados-armadilha na camada selecionada; o tooltip informa quantos. A importação aceita mapas TXT, resultados JSON e métricas globais.',
              'Testes: .venv/Scripts/python -m pytest -q. As análises e figuras usam as mesmas estruturas e resultados dos algoritmos; o HTML não resolve labirintos.']:
        texto(t)
    texto('Modelagem e regras','Heading1')
    texto('G_pos tem um nó por casa não parede. Para comparação, portas são chão ou parede. G_est tem estados (posição, chaves, consumíveis), representados com conjuntos imutáveis. Apenas estados alcançáveis são explorados. Bônus têm IDs por linha e coluna. Rótulo: (3,5)|ab|{0,2}. Coordenadas começam em zero.')
    texto('Movimentos seguem N, L, S, O. Esteiras restringem somente a saída; portas exigem a chave correspondente. O custo é o da casa de destino. G termina o jogo, com apenas o arco virtual de peso zero para ALVO. Métricas excluem ALVO e seus arcos. Passos excluem a ligação virtual. O grafo é dirigido: uma coleta muda o inventário de forma irreversível, e esteiras podem impedir o retorno.')
    story.append(PageBreak());texto('Resultados dos mapas','Heading1')
    tabela([['Mapa','Estados','Arcos','Passos BFS','Custo BF','Armadilhas']]+[[n,str(r['estados']),str(r['arcos']),str(r['passos_bfs']) if r['passos_bfs'] is not None else '-',str(r['custo']) if r['custo'] is not None else '-',str(r['armadilhas'])] for n,r in resumo.items()])
    texto('Comparação de modelagens','Heading1')
    with (pasta/'comparacao_modelagem.csv').open(encoding='utf-8',newline='') as f:linhas=list(csv.DictReader(f))
    tabela([['Mapa','Modelo','Passos','Válido']]+[[r['mapa'],r['abordagem'],r['passos'] or '-',r['caminho_valido']] for r in linhas])
    texto('Portas como chão podem autorizar um percurso antes de coletar a chave. Portas como parede impedem travessias que seriam possíveis após a coleta. O estado registra a mudança e evita essas duas perdas de informação.')
    texto('Bônus consumíveis e prova do m05','Heading1')
    texto('Em qualquer caminho, o conjunto de bônus consumidos só cresce. Num ciclo que retorna ao mesmo estado, esse conjunto precisa terminar igual ao inicial, portanto nenhum bônus pode ser consumido pela primeira vez ao longo do ciclo. No m05, sem fontes repetíveis, todos os movimentos desse ciclo têm custo positivo (inclusive reentradas em bônus já consumidos). Logo nenhum ciclo real de estados tem custo negativo. ALVO não pertence a ciclo porque não possui saída. Em G_pos, atribuir -4 a toda entrada no bônus permite repetir o desconto sem registrar o consumo.')
    texto('m01, m06 e m07','Heading1')
    r1=resumo['m01_terreno'];texto('m01: BFS minimiza movimentos, e não custos. Água e lama tornam um percurso curto mais caro. Consulte os resultados de BFS e Dijkstra para distinguir passos e custo; Bellman-Ford encontra custo '+str(r1['custo'])+'.')
    corrigido=json.loads((pasta/'resultado_m06_fonte_fonte_consumivel.json').read_text(encoding='utf-8'))
    texto('m06: uma entrada na fonte vale -2; sair para chão e retornar custa 1-2=-1. A repetição permite reduzir o custo sem limite. Na opção --fonte-consumivel, a fonte passa a valer 1 após a primeira entrada e seu consumo integra o estado. Bellman-Ford retorna status '+corrigido['status']+' e custo '+str(corrigido['custo'])+'. O ciclo original está em ciclo_negativo_m06.json.')
    texto('m07: a exploração alcança '+str(resumo['m07_impossivel']['estados'])+' estados reais, mas nenhum alcança ALVO. A busca no transposto marca todos esses estados como armadilhas; não há caminho para a saída.')
    story.append(PageBreak());texto('Mapas próprios e conferência manual','Heading1')
    texto('mapa1: corredor com três chaves e portas, uma esteira e um bônus no percurso obrigatório. O teste verifica que a solução de menor custo consome bônus e passa por esteira. mapa2: a proporção de armadilhas é '+str(round(100*resumo['mapa2']['taxa_armadilhas'],2))+'%, acima dos 20% exigidos. Os gabaritos numéricos constam da tabela de resultados.')
    texto('Mapa mínimo SaG, grade 1 por 3: os estados são (0,0)|-|{}, (0,1)|a|{}, (0,0)|a|{} e (0,2)|a|{}. Há quatro arcos reais: S sem chave para a; a para S com chave; S com chave para a; a para G. Com G para ALVO, são cinco arcos e cinco vértices. O teste confere esses números e a mudança de camada.')
    m=json.loads((pasta/'metricas_global.json').read_text(encoding='utf-8'))['m08_grande']['multiplicidade']
    texto('Multiplicidade no m08: máximo '+str(m['maxima'])+', atingido por '+str(m['quantidade_casas_maximas'])+' casas. Não são geradas todas as combinações de inventário: só contam as combinações que conseguem alcançar cada posição pelas portas e pela exploração. Sem bônus nesse mapa, a multiplicidade é o número de conjuntos de chaves alcançáveis naquela casa. Os valores por casa estão em metricas_global.json.')
    for titulo,nome in [('Percurso m03','percurso_m03.png'),('Percurso m08','percurso_m08.png'),('Grafo em camadas m02','camadas_m02.png'),('Árvore BFS m02','arvore_bfs_m02.png'),('Multiplicidade m08','heatmap_m08.png')]:
        story.append(PageBreak());texto(titulo,'Heading1');imagem(nome)
    story.append(PageBreak());texto('Limitações e contribuição','Heading1')
    texto('O grafo de estados pode crescer exponencialmente com chaves e consumíveis. Dijkstra usa seleção linear de vértices, com custo O(V²+E); Bellman-Ford usa O(VE); BFS/DFS usam O(V+E). A classificação DFS é relativa à busca a partir de S. Pesos negativos causam recusa de Dijkstra. O destaque de armadilhas no mapa agrega estados da camada na mesma posição; consulte o CSV para os rótulos exatos.')
    texto('A autoria e a adequação dos mapas próprios devem ser revistas pelo grupo. A interpretação oral, a matriz de contribuição efetiva, a identificação dos integrantes e a declaração assinada são responsabilidades pessoais do grupo e não podem ser inferidas pelo programa. Preencher docs/CONTRIBUICOES.md e incluir a matriz final antes da entrega. A declaração oficial permanece separada e não é assinada nem preenchida por este gerador.')
    def pagina(c,doc):c.setFont('Helvetica',9);c.drawRightString(550,22,str(doc.page))
    SimpleDocTemplate(str(destino),pagesize=(595,842),leftMargin=45,rightMargin=45,topMargin=40,bottomMargin=40).build(story,onFirstPage=pagina,onLaterPages=pagina)
