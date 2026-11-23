"""[IA] Codex – testes da seleção reproduzível e preservação dos arcos."""
import random
import unittest

from src.graphs.graph import Grafo
from src.parte2.amostragem import criar_amostras
from src.parte2.experimentos import medir_algoritmo


class TestAmostragem(unittest.TestCase):
    def setUp(self):
        self.grafo = Grafo(range(20), [(i, i + 1, i - 10) for i in range(19)])

    def test_reproduzivel_aninhada_e_tamanhos(self):
        a = criar_amostras(self.grafo)
        b = criar_amostras(self.grafo)
        self.assertEqual([x['metadados'] for x in a], [x['metadados'] for x in b])
        self.assertEqual([len(x['grafo'].vertices) for x in a], [2, 10, 20])
        self.assertTrue(set(a[0]['grafo'].vertices) <= set(a[1]['grafo'].vertices)
                        <= set(a[2]['grafo'].vertices))

    def test_induzido_preserva_pesos_direcao_paralelos_e_lacos(self):
        self.grafo.adicionar_arco(0, 0, -2)
        self.grafo.adicionar_arco(0, 1, 7)
        antes = (self.grafo.vertices, self.grafo.arestas)
        for item in criar_amostras(self.grafo, obrigatorios=[0, 1]):
            g = item['grafo']
            selecionados = set(g.vertices)
            self.assertEqual(g.arestas, [(u, v, p) for u, v, p in antes[1]
                                        if u in selecionados and v in selecionados])
            self.assertEqual(g.vizinhos(0), [(1, -10), (0, -2), (1, 7)])
        self.assertEqual((self.grafo.vertices, self.grafo.arestas), antes)

    def test_cem_porcento_copia_independente(self):
        g = criar_amostras(self.grafo)[-1]['grafo']
        self.assertEqual(g.vertices, self.grafo.vertices)
        self.assertEqual(g.arestas, self.grafo.arestas)
        g.adicionar_vertice('novo')
        self.assertNotIn('novo', self.grafo.vertices)

    def test_nao_altera_gerador_aleatorio_global(self):
        estado = random.getstate()
        criar_amostras(self.grafo)
        self.assertEqual(random.getstate(), estado)

    def test_arredondamento_isolados_e_grafo_sem_arcos(self):
        a = criar_amostras(Grafo(range(7)))
        self.assertEqual([x['metadados']['vertices'] for x in a], [1, 4, 7])
        self.assertIsNone(a[0]['metadados']['proporcao_arestas_real'])

    def test_parametros_invalidos(self):
        for proporcoes in [[], [0], [1.1], [float('nan')], [True], ['0.5'], [0.5, 0.5]]:
            with self.subTest(proporcoes=proporcoes), self.assertRaises(ValueError):
                criar_amostras(self.grafo, proporcoes)
        for grafo in [Grafo(), Grafo([0])]:
            with self.assertRaises(ValueError):
                criar_amostras(grafo)
        with self.assertRaises(ValueError):
            criar_amostras(self.grafo, semente=True)
        for fixos in [[100], [0, 1, 2]]:
            with self.assertRaises(ValueError):
                criar_amostras(self.grafo, obrigatorios=fixos)

    def test_integracao_com_medidor(self):
        for item in criar_amostras(self.grafo, obrigatorios=[0]):
            g = item['grafo']
            r = medir_algoritmo('BFS', g.vertices, g.arestas, 0,
                                identificacao={'amostragem': item['metadados']})
            self.assertEqual(r['vertices'], item['metadados']['vertices'])
            self.assertEqual(r['arestas'], item['metadados']['arestas'])
            self.assertEqual(r['repeticoes'], 5)
