
import sys
from pathlib import Path

from graphs.io import ler_mapa, exibir_mapa
from graphs.estados import verificar_vizinhos


def main():
    if len(sys.argv) < 2:
        print("Erro: informe o nome do mapa!")
        print("Exemplo: python src/main.py m02_uma_chave")
        return

    nome_mapa = sys.argv[1]

    raiz = Path(__file__).resolve().parent.parent
    caminho = raiz / "mapas" / f"{nome_mapa}.txt"

    try:
        matriz, inicio, fim = ler_mapa(caminho)

    except (FileNotFoundError, ValueError) as erro:
        print(erro)
        return

    exibir_mapa(matriz)

    print("\nPosição inicial:", inicio)
    print("Posição final:", fim)

    vizinhos = verificar_vizinhos(matriz, inicio)

    print("\nVizinhos válidos:", vizinhos)


if __name__ == "__main__":
    main()
