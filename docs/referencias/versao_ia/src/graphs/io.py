"""Leitura de mapas. A leitura do dataset da Parte 2 será adicionada depois.

Coordenadas da grade começam em zero; mensagens usam linhas do arquivo e
colunas a partir de um. Comentários começam com ; na primeira coluna.
Linhas vazias no final são ignoradas; dentro da grade são inválidas.
Espaços não são removidos: não representam casas válidas.
"""

# [IA] Codex – leitura, validação e representação dos dados dos mapas.
from dataclasses import dataclass
from pathlib import Path


Posicao = tuple[int, int]
SIMBOLOS_VALIDOS = frozenset("#.SG,~abcdABCD><^v+*")


class ErroMapa(ValueError):
    """Arquivo ilegível ou mapa que não atende às regras de entrada."""


@dataclass
class Mapa:
    """Grade e posições identificadas durante a leitura, sem estados de jogo.

    Cada chave pode aparecer em mais de uma posição: a validação não impõe
    unicidade de chaves, portas ou saídas, pois o enunciado não a exige.
    """

    grade: tuple[str, ...]
    inicio: Posicao
    saidas: tuple[Posicao, ...]
    chaves: dict[str, tuple[Posicao, ...]]
    bonus: dict[int, Posicao]

    @property
    def altura(self) -> int:
        return len(self.grade)

    @property
    def largura(self) -> int:
        return len(self.grade[0])


def ler_mapa(caminho: str | Path) -> Mapa:
    """Ler arquivo UTF-8 (com ou sem BOM) e retornar um mapa validado.

    Não verifica se há solução: portas sem chave ou saídas isoladas podem
    fazer parte de um mapa válido. Erros são comunicados por ErroMapa.
    """
    caminho = Path(caminho)
    try:
        with caminho.open(encoding="utf-8-sig") as arquivo:
            linhas = [
                (numero, linha.rstrip("\r\n"))
                for numero, linha in enumerate(arquivo, start=1)
                if not linha.startswith(";")
            ]
    except (OSError, UnicodeError) as erro:
        raise ErroMapa(
            f"Não foi possível ler o mapa '{caminho}': {erro}"
        ) from erro

    while linhas and linhas[-1][1] == "":
        linhas.pop()

    if not linhas:
        raise ErroMapa("Mapa inválido: a grade está vazia.")

    largura = len(linhas[0][1])
    inicios: list[Posicao] = []
    saidas: list[Posicao] = []
    chaves: dict[str, list[Posicao]] = {}
    bonus: dict[int, Posicao] = {}

    for linha_grade, (linha_arquivo, conteudo) in enumerate(linhas):
        if not conteudo:
            raise ErroMapa(
                f"Mapa inválido: linha vazia na linha {linha_arquivo} do arquivo."
            )
        if len(conteudo) != largura:
            raise ErroMapa(
                f"Mapa inválido: grade não retangular na linha {linha_arquivo}; "
                f"esperados {largura} caracteres, encontrados {len(conteudo)}."
            )

        for coluna, simbolo in enumerate(conteudo):
            if simbolo not in SIMBOLOS_VALIDOS:
                raise ErroMapa(
                    f"Mapa inválido: símbolo {simbolo!r} na linha "
                    f"{linha_arquivo}, coluna {coluna + 1}."
                )
            posicao = (linha_grade, coluna)
            if simbolo == "S":
                inicios.append(posicao)
            elif simbolo == "G":
                saidas.append(posicao)
            elif simbolo in "abcd":
                chaves.setdefault(simbolo, []).append(posicao)
            elif simbolo == "+":
                bonus[len(bonus)] = posicao

    if len(inicios) != 1:
        raise ErroMapa(
            "Mapa inválido: esperado exatamente um S; "
            f"encontrados {len(inicios)}."
        )
    if not saidas:
        raise ErroMapa("Mapa inválido: esperado pelo menos um G.")

    return Mapa(
        grade=tuple(conteudo for _, conteudo in linhas),
        inicio=inicios[0],
        saidas=tuple(saidas),
        chaves={chave: tuple(posicoes) for chave, posicoes in chaves.items()},
        bonus=bonus,
    )
