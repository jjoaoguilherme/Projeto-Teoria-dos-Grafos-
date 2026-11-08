
caracteres = {
    "#": None,
    ".": 1,
    "S": 1,
    "G": 1,
    ",": 3,
    "~": 5,
    "a": 1,
    "b": 1,
    "c": 1,
    "d": 1,
    "A": 1,
    "B": 1,
    "C": 1,
    "D": 1,
    ">": 1,
    "<": 1,
    "^": 1,
    "v": 1,
    "+": -4,
    "*": -2
}


# LEITURA E VALIDAÇÃO DO MAPA

def ler_mapa(caminho):
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            conteudo = arquivo.read()

    except FileNotFoundError:
        raise FileNotFoundError(
            f"Erro: arquivo '{caminho}' não encontrado!"
        )

    linhas = conteudo.splitlines()
    matriz = [list(linha) for linha in linhas]

    # VALIDAÇÃO DO MAPA

    if len(matriz) == 0:
        raise ValueError("Erro: o mapa está vazio!")

    if len(matriz[0]) == 0:
        raise ValueError("Erro: o mapa não possui colunas!")

    quantidade_inicio = 0
    quantidade_fim = 0

    inicio = None
    fim = None

    for i in range(len(matriz)):

        if len(matriz[i]) == 0:
            raise ValueError(f"Erro: a linha {i} está vazia!")

        if len(matriz[i]) != len(matriz[0]):
            raise ValueError("Erro: o mapa não é retangular!")

        for j in range(len(matriz[i])):
            simbolo = matriz[i][j]

            if simbolo == "S":
                quantidade_inicio += 1
                inicio = (i, j)

            elif simbolo == "G":
                quantidade_fim += 1
                fim = (i, j)

            if simbolo not in caracteres:
                raise ValueError(
                    f"Erro: caractere '{simbolo}' inválido "
                    f"na posição ({i}, {j})!"
                )

    if quantidade_inicio != 1:
        raise ValueError(
            f"Erro: foram encontrados {quantidade_inicio} inícios. "
            "Deve existir exatamente um!"
        )

    if quantidade_fim != 1:
        raise ValueError(
            f"Erro: foram encontradas {quantidade_fim} saídas. "
            "Deve existir exatamente uma!"
        )

    return matriz, inicio, fim


# EXIBIÇÃO DO MAPA

def exibir_mapa(matriz):
    for linha in matriz:
        for simbolo in linha:
            print(caracteres[simbolo], end=" ")
        print()
