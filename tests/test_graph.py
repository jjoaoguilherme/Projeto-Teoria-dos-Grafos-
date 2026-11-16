"""contrato do grafo compartilhado e integração com estados."""
import unittest
from pathlib import Path

from src.graphs.graph import Grafo
from src.graphs.io import ler_mapa
from src.graphs.estados import construir_grafo_estados
from src.graphs.algorithms import bellman_ford, reconstruir_caminho


class TestGrafo(unittest.TestCase):
    def test_dirigido_ordem_e_vertices_sem_saida(self):
        g = Grafo(['S', 'N', 'L', 'B', 'O', 'isolado'])
        for destino in ['N', 'L', 'B', 'O']:
            g.adicionar_arco('S', destino, 1)
        g.adicionar_vertice('S')
        self.assertEqual(g.vertices, ['S', 'N', 'L', 'B', 'O', 'isolado'])
        self.assertEqual(g.vizinhos('S'), [('N', 1), ('L', 1), ('B', 1), ('O', 1)])
        self.assertEqual(g.vizinhos('N'), [])
        self.assertEqual(g.vizinhos('isolado'), [])
        self.assertEqual(g.grau_saida('S'), 4)
        self.assertEqual(g.grau_entrada('S'), 0)
        self.assertEqual(g.grau_entrada('N'), 1)

    def test_arcos_paralelos_lacos_e_pesos_negativos(self):
        g = Grafo(arestas=[('A', 'B', 4), ('A', 'B', -2), ('B', 'B', 0)])
        self.assertEqual(g.vertices, ['A', 'B'])
        self.assertEqual(g.vizinhos('A'), [('B', 4), ('B', -2)])
        self.assertEqual(g.grau_entrada('B'), 3)
        self.assertEqual(g.grau_saida('B'), 1)

    def test_transposto_preserva_vertices_pesos_e_original(self):
        g = Grafo(['A', 'B', 'C', 'isolado'],
                  [('A', 'B', 4), ('A', 'C', -2), ('B', 'C', 1), ('C', 'C', 0)])
        t = g.transposto()
        self.assertEqual(t.vertices, g.vertices)
        self.assertEqual(t.arestas,
                         [('B', 'A', 4), ('C', 'A', -2), ('C', 'B', 1), ('C', 'C', 0)])
        self.assertEqual(t.vizinhos('C'), [('A', -2), ('B', 1), ('C', 0)])
        self.assertEqual(t.vizinhos('isolado'), [])
        self.assertEqual(t.transposto().arestas, g.arestas)
        t.adicionar_arco('isolado', 'A', 2)
        self.assertEqual(g.vizinhos('isolado'), [])
        for v in g.vertices:
            self.assertEqual(g.grau_saida(v), g.transposto().grau_entrada(v))

    def test_consultas_nao_permitem_alterar_estrutura(self):
        g = Grafo(arestas=[('A', 'B', 1)])
        g.vertices.clear()
        g.arestas.clear()
        g.vizinhos('A').clear()
        copia = g.adjacencia
        copia['A'].clear()
        copia['B'].append(('A', 9))
        self.assertEqual(g.adjacencia, {'A': [('B', 1)], 'B': []})
        self.assertEqual(g.arestas, [('A', 'B', 1)])

    def test_pesos_invalidos_nao_alteram_grafo(self):
        g = Grafo()
        for peso in [float('nan'), float('inf'), float('-inf'), None, '1']:
            with self.subTest(peso=peso):
                with self.assertRaises(ValueError):
                    g.adicionar_arco('A', 'B', peso)
                self.assertEqual(g.vertices, [])
                self.assertEqual(g.arestas, [])

    def test_vertice_inexistente(self):
        g = Grafo()
        for consulta in [g.vizinhos, g.grau_entrada, g.grau_saida]:
            with self.assertRaises(KeyError):
                consulta('ausente')

    def test_grafo_vazio(self):
        g = Grafo()
        self.assertEqual(g.adjacencia, {})
        self.assertEqual(g.transposto().vertices, [])
        self.assertEqual(g.transposto().arestas, [])

    def test_bellman_ford_recebe_listas_do_grafo(self):
        g = Grafo('ABCD', [('A', 'B', 4), ('A', 'C', 3),
                           ('C', 'B', -2), ('B', 'D', 5)])
        r = bellman_ford(g.vertices, g.arestas, 'A')
        self.assertEqual(r['distancias']['D'], 6)
        self.assertEqual(reconstruir_caminho(r, 'D'), ['A', 'C', 'B', 'D'])

    def test_estados_preservam_ordem_nlso_e_alvo_terminal(self):
        matriz = [list('...'), list('.S.'), list('..G')]
        dados = construir_grafo_estados(matriz, (1, 1))
        g = dados['grafo']
        self.assertEqual(g.vizinhos(dados['inicio']),
                         [('(0,1)|-|{}', 1), ('(1,2)|-|{}', 1),
                          ('(2,1)|-|{}', 1), ('(1,0)|-|{}', 1)])
        self.assertEqual(g.vizinhos('(2,2)|-|{}'), [('ALVO', 0)])
        self.assertEqual(g.vizinhos('ALVO'), [])
        self.assertEqual(g.vertices, dados['vertices'])
        self.assertEqual(g.arestas, dados['arestas'])

    def test_integracao_com_todos_os_mapas_e_fonte_consumivel(self):
        raiz = Path(__file__).resolve().parents[1]
        caminhos = sorted((raiz / 'data/mapas').glob('*.txt'))
        self.assertEqual(len(caminhos), 8)
        casos = [(p, False) for p in caminhos]
        casos.append((raiz / 'data/mapas/m06_fonte.txt', True))
        for caminho, modo in casos:
            with self.subTest(mapa=caminho.name, fonte_consumivel=modo):
                matriz, inicio, _ = ler_mapa(caminho)
                dados = construir_grafo_estados(matriz, inicio, modo)
                g = dados['grafo']
                self.assertEqual(g.vertices, dados['vertices'])
                self.assertEqual(g.arestas, dados['arestas'])
                self.assertEqual(g.arestas, [(u, v, p) for u, v, _, _, p in dados['registros']])
                self.assertEqual(set(g.vertices), set(dados['estados']) | {'ALVO'})
                self.assertEqual(sum(g.grau_entrada(v) for v in g.vertices), len(g.arestas))
                self.assertEqual(sum(g.grau_saida(v) for v in g.vertices), len(g.arestas))
