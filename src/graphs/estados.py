from collections import deque
from .graph import Grafo

# IDENTIFICAÇÃO DOS VIZINHOS

def verificar_vizinhos(matriz, estado_atual):
    posicao, chaves, bonus_consumidos = estado_atual
    i, j = posicao

    if matriz[i][j] == "G":
        return []
    setas = {">": (0, 1), "<": (0, -1), "^": (-1, 0), "v": (1, 0)}
    if matriz[i][j] in setas:
        di, dj = setas[matriz[i][j]]
        ni, nj = i + di, j + dj
        if not (0 <= ni < len(matriz) and 0 <= nj < len(matriz[0])):
            return []
        simbolo = matriz[ni][nj]
        if simbolo == "#" or (simbolo in "ABCD" and simbolo.lower() not in chaves):
            return []
        return [(ni, nj)]

    vizinhos = []

    cima = (i - 1, j)
    direita = (i, j + 1)
    baixo = (i + 1, j)
    esquerda = (i, j - 1)

    # VERIFICAÇÃO DOS MOVIMENTOS

    # NORTE
    if 0 <= cima[0] < len(matriz) and 0 <= cima[1] < len(matriz[0]):
        if matriz[cima[0]][cima[1]] != "#":

            if matriz[cima[0]][cima[1]] in "ABCD" and matriz[cima[0]][cima[1]].lower() not in chaves:
                pass  # Porta bloqueada
            else:
                vizinhos.append(cima)

    # LESTE
    if 0 <= direita[0] < len(matriz) and 0 <= direita[1] < len(matriz[0]):
        if matriz[direita[0]][direita[1]] != "#":

            if matriz[direita[0]][direita[1]] in "ABCD" and matriz[direita[0]][direita[1]].lower() not in chaves:
                pass  # Porta bloqueada
            else:
                vizinhos.append(direita)

    # SUL
    if 0 <= baixo[0] < len(matriz) and 0 <= baixo[1] < len(matriz[0]):
        if matriz[baixo[0]][baixo[1]] != "#":

            if matriz[baixo[0]][baixo[1]] in "ABCD" and matriz[baixo[0]][baixo[1]].lower() not in chaves:
                pass  # Porta bloqueada
            else:
                vizinhos.append(baixo)

    # OESTE
    if 0 <= esquerda[0] < len(matriz) and 0 <= esquerda[1] < len(matriz[0]):
        if matriz[esquerda[0]][esquerda[1]] != "#":

            if matriz[esquerda[0]][esquerda[1]] in "ABCD" and matriz[esquerda[0]][esquerda[1]].lower() not in chaves:
                pass  # Porta bloqueada
            else:
                vizinhos.append(esquerda)
        


    return vizinhos

def explorar_mapa(matriz, inicio, fim):
    grafo = construir_grafo_estados(matriz, inicio)
    return any(estado[0] == fim for estado in grafo["estados"].values())

def criar_estado(posicao, chaves, bonus_consumidos):
    estado = (posicao, frozenset(chaves), frozenset(bonus_consumidos))
    return estado

def proximo_estado(estado_atual, nova_posicao, matriz):    
    i, j = nova_posicao
    simbolo = matriz[i][j]

    posicao, chaves, bonus_consumidos = estado_atual

    novos_bonus = bonus_consumidos

    novas_chaves = chaves

    if simbolo in "abcd":
        novas_chaves = chaves | {simbolo}

    if simbolo == "+" :
        novos_bonus = bonus_consumidos | {nova_posicao}

    novo_estado = (nova_posicao, novas_chaves, novos_bonus)
    return novo_estado


def construir_grafo_estados(matriz, inicio, fonte_consumivel=False):
    """Explora somente estados alcançáveis; exporta rótulos e arcos dirigidos.

    Mantém posições dos consumíveis internamente e IDs por ordem de leitura
    nos rótulos. Na opção fonte consumível, fontes recebem IDs após os bônus.
    """
    from .io import caracteres

    bonus = [(i, j) for i, linha in enumerate(matriz)
             for j, simbolo in enumerate(linha) if simbolo == "+"]
    fontes = [(i, j) for i, linha in enumerate(matriz)
              for j, simbolo in enumerate(linha) if simbolo == "*"]
    consumiveis = bonus + (fontes if fonte_consumivel else [])
    ids = {posicao: numero for numero, posicao in enumerate(consumiveis)}

    def rotulo(estado):
        (i, j), chaves, consumidos = estado
        numeros = ",".join(str(n) for n in sorted(ids[p] for p in consumidos))
        return f"({i},{j})|{''.join(sorted(chaves)) or '-'}|{{{numeros}}}"

    inicial = criar_estado(inicio, [], [])
    fila = deque([inicial])
    visitados = {inicial}
    estados = {rotulo(inicial): inicial}
    vertices = [rotulo(inicial)]
    arestas = []
    registros = []
    direcoes = {(-1, 0): "N", (0, 1): "L", (1, 0): "S", (0, -1): "O"}
    while fila:
        estado = fila.popleft()
        posicao, _, consumidos = estado
        origem = rotulo(estado)
        i, j = posicao
        if matriz[i][j] == "G":
            arestas.append((origem, "ALVO", 0))
            registros.append((origem, "ALVO", "", "", 0))
            continue
        for destino in verificar_vizinhos(matriz, estado):
            ni, nj = destino
            simbolo = matriz[ni][nj]
            novo_estado = proximo_estado(estado, destino, matriz)
            peso = caracteres[simbolo]
            if simbolo == "+" or (simbolo == "*" and fonte_consumivel):
                peso = 1 if destino in consumidos else caracteres[simbolo]
                novo_estado = criar_estado(destino, novo_estado[1], consumidos | {destino})
            if novo_estado not in visitados:
                visitados.add(novo_estado)
                fila.append(novo_estado)
                estados[rotulo(novo_estado)] = novo_estado
                vertices.append(rotulo(novo_estado))
            alvo = rotulo(novo_estado)
            arestas.append((origem, alvo, peso))
            registros.append((origem, alvo, direcoes[(ni-i, nj-j)], simbolo, peso))
    vertices.append("ALVO")
    grafo = Grafo(vertices, arestas)
    return {"grafo": grafo, "vertices": grafo.vertices,
            "arestas": grafo.arestas, "registros": registros,
            "inicio": rotulo(inicial), "estados": estados}



def construir_grafo_posicoes(matriz, portas="chao"):
    """Cria G_pos de uma matriz já validada, com nós (linha, coluna).

    Inclui casas inalcançáveis e preserva a ordem N, L, S, O dos vizinhos.
    Portas são transitáveis no modo chao e excluídas no modo parede.
    Chaves custam 1; bônus + sempre custam -4; fontes * sempre custam -2.
    Esteiras restringem a saída. G é terminal e não há nó virtual ALVO.
    """
    from .io import caracteres

    if portas not in ("chao", "parede"):
        raise ValueError("O modo de portas deve ser 'chao' ou 'parede'.")

    grafo = Grafo()
    for i, linha in enumerate(matriz):
        for j, simbolo in enumerate(linha):
            if simbolo == "#":
                continue
            if portas == "parede" and simbolo in "ABCD":
                continue
            grafo.adicionar_vertice((i, j))

    # Inventário fixo apenas para reutilizar a geometria dos movimentos:
    # todas as portas liberadas no modo chão, nenhuma no modo parede.
    chaves = frozenset("abcd") if portas == "chao" else frozenset()
    for posicao in grafo.vertices:
        estado_geometrico = (posicao, chaves, frozenset())
        for destino in verificar_vizinhos(matriz, estado_geometrico):
            i, j = destino
            grafo.adicionar_arco(posicao, destino, caracteres[matriz[i][j]])

    return grafo
