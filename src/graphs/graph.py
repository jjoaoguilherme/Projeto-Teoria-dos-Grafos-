"""Grafo dirigido ponderado, independente das regras dos labirintos."""

from math import isfinite


class Grafo:
    """Lista de adjacência com vértices e arcos em ordem de inserção.

    Vértices devem ser hashable (por exemplo, strings, inteiros ou tuplas).
    Cada arco é dirigido: adicionar A -> B não adiciona B -> A.
    Laços, arcos paralelos e pesos negativos finitos são permitidos.
    As consultas retornam cópias para proteger a estrutura interna.
    """

    def __init__(self, vertices=(), arestas=()):
        self._adjacencia = {}
        self._arestas = []
        self._graus_entrada = {}
        for vertice in vertices:
            self.adicionar_vertice(vertice)
        for origem, destino, peso in arestas:
            self.adicionar_arco(origem, destino, peso)

    def adicionar_vertice(self, vertice):
        """Adiciona uma vez; mantém vértices isolados e sem saída."""
        if vertice not in self._adjacencia:
            self._adjacencia[vertice] = []
            self._graus_entrada[vertice] = 0

    def adicionar_arco(self, origem, destino, peso):
        """Adiciona o arco e cria seus extremos caso ainda não existam.

        Repetições são preservadas, não substituídas nem espelhadas.
        """
        if not isinstance(peso, (int, float)) or not isfinite(peso):
            raise ValueError("O peso deve ser um número finito (int ou float).")
        # Valida ambos antes de alterar o grafo.
        hash(origem)
        hash(destino)
        self.adicionar_vertice(origem)
        self.adicionar_vertice(destino)
        self._adjacencia[origem].append((destino, peso))
        self._arestas.append((origem, destino, peso))
        self._graus_entrada[destino] += 1

    @property
    def vertices(self):
        """Lista de todos os vértices na ordem de inserção."""
        return list(self._adjacencia)

    @property
    def arestas(self):
        """Lista de (origem, destino, peso), compatível com Bellman-Ford."""
        return list(self._arestas)

    @property
    def adjacencia(self):
        """Cópia do dicionário {vertice: [(destino, peso), ...]}."""
        return {vertice: list(vizinhos)
                for vertice, vizinhos in self._adjacencia.items()}

    def vizinhos(self, vertice):
        """Pares (destino, peso) em ordem de inserção; KeyError se não existe."""
        return list(self._adjacencia[vertice])

    def grau_entrada(self, vertice):
        """Número de arcos que chegam, contando arcos paralelos."""
        return self._graus_entrada[vertice]

    def grau_saida(self, vertice):
        """Número de arcos que saem, contando arcos paralelos."""
        return len(self._adjacencia[vertice])

    def transposto(self):
        """Novo grafo com todos os arcos invertidos e os mesmos pesos.

        Preserva todos os vértices; a ordem dos novos arcos segue a original.
        O grafo original não é alterado.
        """
        return Grafo(self.vertices, ((v, u, peso) for u, v, peso in self._arestas))
