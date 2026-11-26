"""[IA] Codex – consolidação reproduzível das sessões de desempenho."""
import argparse
import json
from pathlib import Path

from .verificar_experimentos import (
    RELATORIO_CONSOLIDADO, RELATORIO_ESCALABILIDADE,
    listar_relatorios_origem, verificar_relatorio,
)


def consolidar_relatorios(pasta='out/parte2'):
    pasta = Path(pasta)
    nomes = listar_relatorios_origem(pasta)
    experimentos, sessoes = [], []
    for nome in nomes:
        dados = json.loads((pasta / nome).read_text(encoding='utf-8-sig'))
        verificacao = verificar_relatorio(dados)
        if not verificacao['valido']:
            raise ValueError(f'{nome}: ' + '; '.join(verificacao['erros']))
        if nome == RELATORIO_ESCALABILIDADE:
            from .graficos_escalabilidade import preparar_escalabilidade
            preparar_escalabilidade(dados)
        sessao = {k: v for k, v in dados.items() if k != 'experimentos'}
        sessao.update(arquivo_origem=nome, inicio_experimentos=len(experimentos),
                      quantidade_experimentos=len(dados['experimentos']))
        sessoes.append(sessao)
        experimentos.extend(dados['experimentos'])
    consolidado = {'versao_formato': 1, 'demonstracao': False,
                   'experimentos': experimentos, 'sessoes': sessoes}
    destino = pasta / RELATORIO_CONSOLIDADO
    destino.write_text(json.dumps(consolidado, ensure_ascii=False, indent=2,
                                  allow_nan=False) + '\n', encoding='utf-8')
    return destino


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pasta', default='out/parte2')
    args = parser.parse_args()
    try:
        print(consolidar_relatorios(args.pasta))
    except (ValueError, OSError) as erro:
        parser.exit(1, f'Erro: {erro}\n')


if __name__ == '__main__':
    main()
