"""Leitura do TSV Reddit e construção de grafo dirigido com atributos."""
import argparse
import csv
import json
from pathlib import Path

from ..graphs.graph import Grafo
from .qualidade import iniciar_qualidade, conferir_atributos

COLUNAS_OBRIGATORIAS = {'SOURCE_SUBREDDIT', 'TARGET_SUBREDDIT', 'LINK_SENTIMENT'}


def _processar_dataset(caminho, construir, invalidos):
    if invalidos not in {'erro', 'registrar'}:
        raise ValueError("Política de inválidos deve ser 'erro' ou 'registrar'.")
    caminho = Path(caminho)
    if not caminho.is_file():
        raise FileNotFoundError(f'Arquivo não encontrado: {caminho}')
    grafo = Grafo() if construir else None
    atributos = []
    contagens = dict.fromkeys(['registros', 'validos', 'invalidos', 'negativos',
                              'nao_negativos', 'lacos', 'pares_repetidos'], 0)
    erros = []
    vertices = set()
    pares = set()
    motivos = {}
    with caminho.open('r', encoding='utf-8-sig', newline='') as arquivo:
        leitor = csv.DictReader(arquivo, delimiter='\t')
        cabecalho = leitor.fieldnames or []
        if len(set(cabecalho)) != len(cabecalho):
            raise ValueError('Cabeçalho contém colunas repetidas.')
        faltantes = COLUNAS_OBRIGATORIAS - set(cabecalho)
        if faltantes:
            raise ValueError('Colunas obrigatórias ausentes: ' + ', '.join(sorted(faltantes)))
        qualidade = iniciar_qualidade(cabecalho)
        assinaturas = set()
        for registro in leitor:
            linha = leitor.line_num
            contagens['registros'] += 1
            conferir_atributos(registro, qualidade, assinaturas, linha)
            origem = (registro.get('SOURCE_SUBREDDIT') or '').strip()
            destino = (registro.get('TARGET_SUBREDDIT') or '').strip()
            sentimento = (registro.get('LINK_SENTIMENT') or '').strip()
            motivo = None
            if None in registro or any(v is None for v in registro.values()):
                motivo = 'quantidade de campos diferente do cabeçalho'
            elif not origem or not destino:
                motivo = 'origem ou destino ausente'
            elif sentimento not in {'-1', '1'}:
                motivo = 'sentimento deve ser -1 ou 1'
            if motivo:
                contagens['invalidos'] += 1
                motivos[motivo] = motivos.get(motivo, 0) + 1
                if invalidos == 'erro':
                    raise ValueError(f'Linha {linha} inválida: {motivo}.')
                erros.append({'linha': linha, 'motivo': motivo, 'registro': registro})
                continue
            peso = int(sentimento)
            contagens['validos'] += 1
            contagens['negativos' if peso < 0 else 'nao_negativos'] += 1
            contagens['lacos'] += origem == destino
            contagens['pares_repetidos'] += (origem, destino) in pares
            pares.add((origem, destino))
            vertices.update([origem, destino])
            if construir:
                grafo.adicionar_arco(origem, destino, peso)
                atributos.append({'linha': linha, 'atributos': registro})
    relatorio = {
        'arquivo': str(caminho), 'colunas': cabecalho,
        'contagens': contagens, 'vertices': len(vertices), 'arestas': contagens['validos'],
        'pares_distintos': len(pares), 'politica_invalidos': invalidos,
        'motivos_invalidos': motivos,
        'linhas_invalidas_exemplo': [e['linha'] for e in erros[:5]],
        'atinge_20_mil_arestas': contagens['validos'] >= 20000,
        'acima_500_mil_arestas': contagens['validos'] > 500000,
        'pesos': 'LINK_SENTIMENT sem transformação (-1 ou 1)',
        'politica_repeticoes': 'Preservar cada registro como arco, inclusive paralelos e laços.',
        'qualidade': qualidade,
        'colunas_base_avd': ['linha_arquivo'] + [c for c in cabecalho if c != 'PROPERTIES'],
    }
    return {'grafo': grafo, 'atributos_arestas': atributos,
            'registros_invalidos': erros, 'relatorio': relatorio}


def verificar_dataset(caminho):
    """Conta válidos/inválidos sem construir o grafo, preservando a API anterior."""
    return _processar_dataset(caminho, construir=False, invalidos='registrar')['relatorio']


def carregar_dataset(caminho, invalidos='erro'):
    """Retorna grafo, atributos alinhados aos arcos e relatório de qualidade.

    Padrão estrito: não retorna um grafo parcial se houver registro inválido.
    O modo registrar é explícito e retém as linhas rejeitadas para revisão.
    Não agrega arcos repetidos nem inventa pesos, direção ou atributos.
    """
    return _processar_dataset(caminho, construir=True, invalidos=invalidos)


def exportar_dataset(dados, pasta):
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / 'resumo_dataset.json').write_text(
        json.dumps(dados['relatorio'], ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    with (pasta / 'arestas_dataset.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.writer(f);w.writerow(['origem', 'destino', 'peso'])
        w.writerows(dados['grafo'].arestas)
    (pasta / 'registros_invalidos.json').write_text(
        json.dumps(dados['registros_invalidos'], ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    colunas = dados['relatorio']['colunas_base_avd']
    with (pasta / 'base_avd.csv').open('w', encoding='utf-8', newline='') as f:
        escritor = csv.DictWriter(f, fieldnames=colunas)
        escritor.writeheader()
        for atributo, (origem, destino, peso) in zip(dados['atributos_arestas'], dados['grafo'].arestas):
            linha = {c: atributo['atributos'].get(c, '') for c in colunas if c != 'linha_arquivo'}
            linha.update(linha_arquivo=atributo['linha'], SOURCE_SUBREDDIT=origem,
                         TARGET_SUBREDDIT=destino, LINK_SENTIMENT=peso)
            escritor.writerow(linha)



def main():
    parser = argparse.ArgumentParser(description='Verificar ou construir o grafo do TSV Reddit')
    parser.add_argument('--arquivo', required=True)
    parser.add_argument('--construir', action='store_true')
    parser.add_argument('--invalidos', choices=['erro', 'registrar'], default='erro')
    parser.add_argument('--out', help='Exportar resumo e arcos; exige --construir')
    args = parser.parse_args()
    if args.out and not args.construir:
        parser.error('--out exige --construir.')
    try:
        if args.construir:
            dados = carregar_dataset(args.arquivo, args.invalidos)
            if args.out: exportar_dataset(dados, args.out)
            resultado = dados['relatorio']
        else:
            resultado = verificar_dataset(args.arquivo)
    except (OSError, ValueError, csv.Error) as erro:
        parser.exit(1, f'Erro: {erro}\n')
    print(json.dumps(resultado, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
