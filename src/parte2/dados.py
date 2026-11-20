"""Leitura e validação inicial do dataset Reddit Hyperlink Network.

[IA] ChatGPT — apoio com sintaxe de leitura TSV e tratamento de erros.
Não implementa algoritmos, experimentos nem interpretações analíticas.
"""

import argparse
import csv
import json
from pathlib import Path

COLUNAS_OBRIGATORIAS = {
    "SOURCE_SUBREDDIT", "TARGET_SUBREDDIT", "LINK_SENTIMENT",
}


def verificar_dataset(caminho):
    caminho = Path(caminho)
    if not caminho.is_file():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    contagens = {"registros": 0, "validos": 0, "invalidos": 0,
                 "negativos": 0, "nao_negativos": 0}
    exemplos_invalidos = []

    with caminho.open("r", encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo, delimiter="\t")
        colunas = set(leitor.fieldnames or [])
        faltantes = COLUNAS_OBRIGATORIAS - colunas
        if faltantes:
            raise ValueError("Colunas obrigatórias ausentes: " + ", ".join(sorted(faltantes)))

        for numero_linha, registro in enumerate(leitor, start=2):
            contagens["registros"] += 1
            origem = (registro.get("SOURCE_SUBREDDIT") or "").strip()
            destino = (registro.get("TARGET_SUBREDDIT") or "").strip()
            rotulo = (registro.get("LINK_SENTIMENT") or "").strip()
            if not origem or not destino or rotulo not in {"-1", "1"}:
                contagens["invalidos"] += 1
                if len(exemplos_invalidos) < 5:
                    exemplos_invalidos.append(numero_linha)
                continue
            contagens["validos"] += 1
            if rotulo == "-1":
                contagens["negativos"] += 1
            else:
                contagens["nao_negativos"] += 1

    return {"arquivo": str(caminho), "contagens": contagens,
            "linhas_invalidas_exemplo": exemplos_invalidos}


def main():
    parser = argparse.ArgumentParser(description="Verificar TSV do Reddit")
    parser.add_argument("--arquivo", required=True, help="Caminho para o arquivo TSV")
    args = parser.parse_args()
    try:
        resultado = verificar_dataset(args.arquivo)
    except (OSError, ValueError) as erro:
        parser.exit(1, f"Erro: {erro}\n")
    print(json.dumps(resultado, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
