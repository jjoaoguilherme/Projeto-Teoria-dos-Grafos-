import os
os.system("cls")

def encerrar():
    print("\n- Programa encerrado -")
    exit()

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

# LEITURA DO MAPA

with open("mapas/m02_uma_chave.txt", "r", encoding="utf-8") as arquivo:
    conteudo = arquivo.read()

linhas = conteudo.splitlines()
matriz = [list(linha) for linha in linhas]

# VALIDAÇÂO DO MAPA
    
if len(matriz) == 0:
    print("Erro: o mapa está vazio!")
    encerrar()

for i in range(len(matriz)):
    if len(matriz[i]) != len(matriz[0]):
        print("Erro: o mapa não é retangular!")
        encerrar()

    for j in range(len(matriz[i])):
        simbolo = matriz[i][j]

        if simbolo not in caracteres:
            print(f"Erro: caractere '{simbolo}' inválido na posição ({i}, {j})!")
            encerrar()

# IDENTIFICAÇÃO DAS POSIÇÕES E EXIBIÇÃO DO MAPA

for i in range(len(matriz)):
    for j in range(len(matriz[i])):
        simbolo = matriz[i][j]

        if simbolo == "S":
            inicio = (i, j)

        elif simbolo == "G":
            fim = (i, j)

        print(caracteres[simbolo], end=" ")
    print()

print("\nPosição inicial:", inicio)
print("Posição final:", fim)