"""Entrada compatível com os comandos exigidos pelo enunciado."""
import sys
from .main import main as main_parte1


def main():
    # [IA] ChatGPT – direciona a interface da Parte 2 sem alterar a Parte 1.
    if any(a == '--dataset' or a.startswith('--dataset=') or a == '--benchmark'
           for a in sys.argv[1:]):
        from .parte2.cli import main as main_parte2
        main_parte2()
    else:
        main_parte1()


if __name__ == '__main__':
    main()
