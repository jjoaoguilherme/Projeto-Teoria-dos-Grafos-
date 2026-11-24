"""Relatório técnico da obtenção, qualidade e modelagem dos dados da Parte 2."""
from pathlib import Path
from xml.sax.saxutils import escape


def gerar_relatorio_dados(resumo, destino):
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    estilos = getSampleStyleSheet()
    estilos.add(ParagraphStyle('TextoDados', fontName='Helvetica', fontSize=10,
                              leading=14, spaceAfter=9, alignment=TA_LEFT))
    estilos.add(ParagraphStyle('CelulaDados', fontName='Helvetica', fontSize=8.5, leading=11))
    story = []
    verde = colors.HexColor('#125d4b')
    for nome in ['Heading1', 'Heading2']:
        estilos[nome].textColor = verde
        estilos[nome].keepWithNext = True

    def texto(conteudo, estilo='TextoDados'):
        story.append(Paragraph(escape(str(conteudo)), estilos[estilo]))

    def tabela(linhas, larguras):
        celulas = [[Paragraph(escape(str(v)), estilos['CelulaDados']) for v in linha] for linha in linhas]
        t = Table(celulas, colWidths=larguras, repeatRows=1, hAlign='LEFT')
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8f1e9')),
            ('GRID', (0, 0), (-1, -1), .35, colors.HexColor('#dce3db')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ]))
        story.extend([t, Spacer(1, 12)])

    def numero(valor):
        return f'{valor:,}'.replace(',', '.')

    contagens = resumo['contagens']
    qualidade = resumo['qualidade']
    origem = resumo.get('origem', {})
    texto('Preparação do dataset - Parte 2', 'Title')
    texto('Dados e construção do grafo', 'Heading2')
    texto('Este documento registra a obtenção do arquivo aprovado, as verificações de qualidade e a representação fornecida aos algoritmos e à análise de dados. Não apresenta os experimentos ou as conclusões de AVD.')
    texto('1. Fonte e reprodução', 'Heading1')
    texto('Dataset: Reddit Hyperlink Network, arquivo de links nos títulos. A aprovação deste arquivo foi confirmada por João em 24/11/2026.')
    texto('Página da fonte: ' + origem.get('fonte', ''))
    texto('Download: ' + origem.get('url_download', ''))
    texto('SHA-256: ' + origem.get('sha256', 'não registrado'))
    texto('O script baixa o arquivo da fonte oficial. Nas próximas execuções, confere o arquivo local pelo SHA-256 salvo no manifesto. O TSV grande fica fora do Git; o script e o manifesto permitem reproduzir a obtenção.')
    texto('Comando único, executado na raiz do projeto:')
    texto('python -m src.parte2.preparar')
    texto('2. Conferência do arquivo real', 'Heading1')
    tabela([['Item verificado', 'Resultado'],
            ['Registros lidos', numero(contagens['registros'])],
            ['Vértices (comunidades)', numero(resumo['vertices'])],
            ['Arcos válidos (registros)', numero(resumo['arestas'])],
            ['Registros inválidos para o grafo', numero(contagens['invalidos'])],
            ['Pesos -1 / pesos +1', f"{numero(contagens['negativos'])} / {numero(contagens['nao_negativos'])}"],
            ['Pares origem-destino distintos', numero(resumo['pares_distintos'])],
            ['Repetições de pares / laços', f"{numero(contagens['pares_repetidos'])} / {numero(contagens['lacos'])}"],
            ['Duplicatas exatas do registro inteiro', numero(qualidade['duplicatas_exatas'])]], [310, 200])

    story.append(PageBreak())
    texto('3. Qualidade e tratamento', 'Heading1')
    tabela([['Coluna', 'Faltantes', 'Espaços externos'],
            *[[c, numero(n), numero(qualidade['espacos_externos_por_coluna'][c])]
              for c, n in qualidade['faltantes_por_coluna'].items()]], [290, 100, 120])
    props = qualidade['properties']
    texto('Datas não interpretáveis: ' + numero(qualidade['datas_invalidas']) + '. Vetores PROPERTIES inválidos (dimensão diferente de 86 ou valores não finitos/não numéricos): ' + numero(props['vetores_invalidos']) + '.')
    texto('Dimensões dos vetores encontradas: ' + ', '.join(f'{d} atributos em {numero(n)} registros' for d, n in props['dimensoes_encontradas'].items()) + '.')
    texto('Campos vazios e espaços externos são contados por coluna. Valores originais continuam no TSV e nos atributos em memória. Apenas os identificadores de origem/destino e o peso são normalizados para a representação do grafo.')
    texto('Uma linha sem origem/destino, com sentimento fora de {-1, 1} ou com número incorreto de campos interrompe a preparação padrão. Não há exclusão silenciosa. O modo opcional de registro de inválidos preserva as linhas rejeitadas para revisão, sem presumir uma justificativa para apagá-las.')
    texto('Datas e vetores auxiliares são conferidos e sinalizados. Nenhum valor auxiliar é imputado ou removido automaticamente. A análise de AVD deve avaliar esses atributos e a necessidade de tratamento segundo a pergunta de pesquisa.')
    texto('Arcos paralelos são mantidos: publicações diferentes podem citar o mesmo par de comunidades. Laços também são mantidos. Duplicatas exatas são contadas e preservadas, pois o leitor não presume que registros iguais devam ser descartados. As contagens de arcos representam registros, não pares únicos.')
    if resumo['acima_500_mil_arestas']:
        texto('A base passa de 500 mil arcos. A amostragem para escalabilidade já existe em src/parte2/amostragem.py; executar e justificar os três tamanhos pertence à etapa de experimentos. O leitor entrega a base completa e não inventa ou elimina ligações para reduzir seu tamanho.')

    story.append(PageBreak())
    texto('4. Como os dados viram grafo', 'Heading1')
    tabela([['Elemento do TSV', 'Representação'],
            ['Comunidades de origem e destino', 'SOURCE_SUBREDDIT e TARGET_SUBREDDIT identificam os vértices.'],
            ['Cada registro', 'Um arco dirigido da origem para o destino. Não se cria automaticamente o arco reverso.'],
            ['LINK_SENTIMENT = -1', 'Referência explicitamente negativa. Peso original -1.'],
            ['LINK_SENTIMENT = +1', 'Referência neutra ou positiva. Peso original +1.'],
            ['POST_ID, TIMESTAMP e PROPERTIES', 'Atributos preservados para a análise de dados.']], [245, 265])
    texto('Um caminho A -> B -> C representa uma sequência de referências entre comunidades. Seu custo é a soma dos pesos originais. Como cada peso é +1 ou -1, a soma equivale à quantidade de referências não negativas menos a quantidade de referências negativas nesse caminho. Menor soma não significa uma relação mais amigável.')
    texto('Um ciclo negativo volta ao vértice inicial com soma de pesos menor que zero. Repetir matematicamente esse ciclo reduz a soma sem limite. Isso é uma propriedade da modelagem por pesos assinados, e não uma distância física. A detecção e os recortes de teste são apresentados nos experimentos do grupo.')
    texto('A classificação refere-se a cada publicação, não a uma amizade ou inimizade permanente entre comunidades. Os algoritmos atuais usam a rede agregada e não impõem ordem cronológica aos links; um caminho estrutural não comprova transmissão temporal ou causalidade.')
    texto('5. Arquivos para o grupo', 'Heading1')
    tabela([['Arquivo / acesso', 'Utilidade'],
            ['out/parte2/resumo_dataset.json', 'Contagens, qualidade e identificação da fonte.'],
            ['out/parte2/arestas_dataset.csv', 'Origem, destino e peso de todos os arcos.'],
            ['out/parte2/base_avd.csv', 'Metadados tabulares das linhas válidas, com número da linha original. PROPERTIES permanece no TSV e na API.'],
            ['out/parte2/registros_invalidos.json', 'Registros rejeitados, quando houver.'],
            ['carregar_dataset(caminho)', 'Devolve grafo, atributos completos e relatório para os demais módulos.']], [245, 265])
    texto('Para explicar: baixamos o arquivo aprovado, conferimos seus campos, transformamos comunidades em vértices e referências em arcos, preservamos os pesos e fornecemos os dados validados para os algoritmos e para AVD.')

    def rodape(canvas, doc):
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#536763'))
        canvas.drawString(42, 22, 'Preparação dos dados - Parte 2')
        canvas.drawRightString(A4[0] - 42, 22, str(doc.page))

    SimpleDocTemplate(str(destino), pagesize=A4, leftMargin=42, rightMargin=42,
                      topMargin=38, bottomMargin=38).build(story, onFirstPage=rodape, onLaterPages=rodape)
    return destino
