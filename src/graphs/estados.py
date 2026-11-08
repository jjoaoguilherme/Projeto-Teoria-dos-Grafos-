
# IDENTIFICAÇÃO DOS VIZINHOS

def verificar_vizinhos(matriz, posicao):
    i, j = posicao

    vizinhos = []

    cima = (i - 1, j)
    direita = (i, j + 1)
    baixo = (i + 1, j)
    esquerda = (i, j - 1)

    # VERIFICAÇÃO DOS MOVIMENTOS

    # NORTE
    if 0 <= cima[0] < len(matriz) and 0 <= cima[1] < len(matriz[0]):
        if matriz[cima[0]][cima[1]] != "#":
            vizinhos.append(cima)

    # LESTE
    if 0 <= direita[0] < len(matriz) and 0 <= direita[1] < len(matriz[0]):
        if matriz[direita[0]][direita[1]] != "#":
            vizinhos.append(direita)

    # SUL
    if 0 <= baixo[0] < len(matriz) and 0 <= baixo[1] < len(matriz[0]):
        if matriz[baixo[0]][baixo[1]] != "#":
            vizinhos.append(baixo)

    # OESTE
    if 0 <= esquerda[0] < len(matriz) and 0 <= esquerda[1] < len(matriz[0]):
        if matriz[esquerda[0]][esquerda[1]] != "#":
            vizinhos.append(esquerda)

    return vizinhos
