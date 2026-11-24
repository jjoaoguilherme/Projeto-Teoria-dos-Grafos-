"""Download do arquivo de títulos do Reddit disponibilizado pelo SNAP."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

NOME = 'soc-redditHyperlinks-title.tsv'
URL = 'https://snap.stanford.edu/data/' + NOME
FONTE = 'https://snap.stanford.edu/data/soc-RedditHyperlinks.html'
DESTINO = Path('data/dataset_parte2') / NOME


def calcular_sha256(caminho):
    resumo = hashlib.sha256()
    with Path(caminho).open('rb') as arquivo:
        for bloco in iter(lambda: arquivo.read(1024 * 1024), b''):
            resumo.update(bloco)
    return resumo.hexdigest()


def conferir_cabecalho(caminho):
    with Path(caminho).open(encoding='utf-8-sig') as arquivo:
        cabecalho = arquivo.readline().strip().split('\t')
    obrigatorias = {'SOURCE_SUBREDDIT', 'TARGET_SUBREDDIT', 'LINK_SENTIMENT'}
    if not obrigatorias.issubset(cabecalho):
        raise ValueError('O arquivo recebido não contém as colunas esperadas do Reddit.')
    return cabecalho


def obter_dataset(destino=DESTINO):
    """Baixa uma vez e confere a identidade do arquivo pelo manifesto salvo."""
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    manifesto = destino.parent / 'origem_dataset.json'
    origem = json.loads(manifesto.read_text(encoding='utf-8')) if manifesto.exists() else {}
    esperado = origem.get('sha256')
    if destino.exists():
        sha256 = calcular_sha256(destino)
        if esperado and sha256 != esperado:
            raise ValueError('O TSV local difere do SHA-256 registrado em origem_dataset.json.')
        print('Arquivo local encontrado e conferido.', flush=True)
    else:
        parcial = destino.with_suffix('.tsv.part')
        print('Baixando o TSV da fonte oficial do SNAP...', flush=True)
        with urlopen(URL, timeout=45) as resposta, parcial.open('wb') as arquivo:
            tamanho = int(resposta.headers.get('Content-Length', 0))
            recebido = 0
            proximo_aviso = 32 * 1024 * 1024
            while bloco := resposta.read(1024 * 1024):
                arquivo.write(bloco)
                recebido += len(bloco)
                if recebido >= proximo_aviso:
                    print(f'{recebido // (1024 * 1024)} MiB recebidos', flush=True)
                    proximo_aviso += 32 * 1024 * 1024
        if tamanho and recebido != tamanho:
            raise ValueError('Download incompleto. Execute novamente para repetir o download.')
        sha256 = calcular_sha256(parcial)
        if esperado and sha256 != esperado:
            raise ValueError('O download difere do SHA-256 registrado. O TSV não foi substituído.')
        conferir_cabecalho(parcial)
        parcial.replace(destino)
        origem['obtido_em_utc'] = datetime.now(timezone.utc).isoformat()
    cabecalho = conferir_cabecalho(destino)
    origem.update({'dataset': 'Reddit Hyperlink Network — links nos títulos',
                   'arquivo': destino.name, 'fonte': FONTE, 'url_download': URL,
                   'sha256': sha256, 'tamanho_bytes': destino.stat().st_size,
                   'colunas': cabecalho})
    manifesto.write_text(json.dumps(origem, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return destino


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destino', default=str(DESTINO))
    args = parser.parse_args()
    try:
        print(obter_dataset(args.destino))
    except (OSError, ValueError) as erro:
        parser.exit(1, f'Erro: {erro}\n')


if __name__ == '__main__':
    main()
