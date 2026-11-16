"""testes do Bellman-Ford e reconstrução de caminhos."""
import unittest
from src.graphs.algorithms import bellman_ford, reconstruir_caminho


class TestBellmanFord(unittest.TestCase):
    def test_exemplo_usuario(self):
        arestas = [('A', 'B', 4), ('A', 'C', 3), ('C', 'B', -2),
                   ('B', 'D', 5), ('C', 'D', 6)]
        r = bellman_ford('ABCD', arestas, 'A')
        self.assertEqual(r['distancias'], {'A': 0, 'B': 1, 'C': 3, 'D': 6})
        self.assertEqual(reconstruir_caminho(r, 'D'), ['A', 'C', 'B', 'D'])
        self.assertFalse(r['tem_ciclo_negativo'])

    def test_ordem_inversa(self):
        r = bellman_ford('ABCD', [('C', 'D', 1), ('B', 'C', 1), ('A', 'B', 1)], 'A')
        self.assertEqual(r['distancias']['D'], 3)

    def test_ciclo_negativo(self):
        arestas = [('A', 'B', 1), ('B', 'C', -3), ('C', 'B', 1),
                   ('C', 'D', 2), ('A', 'E', 7)]
        r = bellman_ford('ABCDE', arestas, 'A')
        self.assertTrue(r['tem_ciclo_negativo'])
        self.assertEqual(r['ciclo_negativo'][0], r['ciclo_negativo'][-1])
        self.assertLess(r['custo_ciclo'], 0)
        self.assertEqual(r['custo_ciclo'], sum(e[2] for e in r['arestas_ciclo']))
        self.assertTrue(all(e in arestas for e in r['arestas_ciclo']))
        self.assertEqual(r['afetados_ciclo_negativo'], {'B', 'C', 'D'})
        for u, v, _ in r['arestas_ciclo']:
            self.assertIn((u, v), list(zip(r['ciclo_negativo'], r['ciclo_negativo'][1:])))
        with self.assertRaises(ValueError):
            reconstruir_caminho(r, 'D')
        self.assertEqual(reconstruir_caminho(r, 'E'), ['A', 'E'])

    def test_ciclo_inalcancavel(self):
        r = bellman_ford('ABC', [('B', 'C', -2), ('C', 'B', 1)], 'A')
        self.assertFalse(r['tem_ciclo_negativo'])
        self.assertEqual(reconstruir_caminho(r, 'B'), [])
        self.assertEqual(reconstruir_caminho(r, 'A'), ['A'])

    def test_laco_negativo_paralelo(self):
        r = bellman_ford([0], [(0, 0, 2), (0, 0, -1)], 0)
        self.assertEqual(r['ciclo_negativo'], [0, 0])
        self.assertEqual(r['custo_ciclo'], -1)

    def test_ciclo_zero(self):
        r = bellman_ford('AB', [('A', 'B', -1), ('B', 'A', 1)], 'A')
        self.assertFalse(r['tem_ciclo_negativo'])
        self.assertEqual(r['distancias']['B'], -1)

    def test_entradas_invalidas(self):
        for vertices, arestas, inicio in [([], [], 'A'),
                                         (['A'], [('A', 'B', 1)], 'A'),
                                         (['A'], [('A', 'A', float('nan'))], 'A')]:
            with self.subTest(arestas=arestas):
                with self.assertRaises(ValueError):
                    bellman_ford(vertices, arestas, inicio)
