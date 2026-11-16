"""Testes do grafo de posições e dos dois tratamentos das portas."""
from pathlib import Path
import unittest

from src.graphs.estados import construir_grafo_posicoes
from src.graphs.graph import Grafo
from src.graphs.io import ler_mapa


class TestGrafoPosicoes(unittest.TestCase):
    def test_grafo_pequeno_contado_a_mao(self):
        g = construir_grafo_posicoes(['S.G'])
        self.assertIsInstance(g, Grafo)
        self.assertEqual(g.vertices, [(0, 0), (0, 1), (0, 2)])
        self.assertEqual(g.arestas, [((0, 0), (0, 1), 1),
                                   ((0, 1), (0, 2), 1),
                                   ((0, 1), (0, 0), 1)])
        self.assertNotIn('ALVO', g.vertices)

    def test_inclui_casas_inalcancaveis(self):
        g = construir_grafo_posicoes(['S#G'])
        self.assertEqual(g.vertices, [(0, 0), (0, 2)])
        self.assertEqual(g.arestas, [])

    def test_portas_como_chao_sem_coleta(self):
        g = construir_grafo_posicoes(['SA.aG'])
        self.assertEqual(len(g.vertices), 5)
        self.assertEqual(len(g.arestas), 7)
        self.assertEqual(g.vizinhos((0, 0)), [((0, 1), 1)])

    def test_portas_como_parede(self):
        g = construir_grafo_posicoes(['SA.aG'], portas='parede')
        self.assertEqual(g.vertices, [(0, 0), (0, 2), (0, 3), (0, 4)])
        self.assertEqual(g.arestas, [((0, 2), (0, 3), 1),
                                   ((0, 3), (0, 4), 1),
                                   ((0, 3), (0, 2), 1)])
        self.assertEqual(g.vizinhos((0, 0)), [])

    def test_pesos_de_destino_e_bonus_fixo(self):
        g = construir_grafo_posicoes(['S,~aA+*G'])
        self.assertEqual(g.vizinhos((0, 1)), [((0, 2), 5), ((0, 0), 1)])
        for arco in [((0, 0), (0, 1), 3), ((0, 2), (0, 3), 1),
                     ((0, 3), (0, 4), 1), ((0, 4), (0, 5), -4),
                     ((0, 6), (0, 5), -4), ((0, 5), (0, 6), -2),
                     ((0, 6), (0, 7), 1)]:
            self.assertIn(arco, g.arestas)

    def test_ordem_norte_leste_sul_oeste(self):
        g = construir_grafo_posicoes(['...', '.S.', '..G'])
        self.assertEqual(g.vizinhos((1, 1)),
                         [((0, 1), 1), ((1, 2), 1), ((2, 1), 1), ((1, 0), 1)])

    def test_esteiras_quatro_direcoes_e_entrada_livre(self):
        for simbolo, destino in [('^', (0, 1)), ('>', (1, 2)),
                                 ('v', (2, 1)), ('<', (1, 0))]:
            with self.subTest(simbolo=simbolo):
                g = construir_grafo_posicoes(['..G', '.'+simbolo+'.', 'S..'])
                self.assertEqual(g.vizinhos((1, 1)), [(destino, 1)])
                for origem in [(0, 1), (1, 0), (1, 2), (2, 1)]:
                    self.assertIn(((1, 1), 1), g.vizinhos(origem))

    def test_esteira_contra_parede_ou_borda(self):
        for linha in ['S>#G', 'G.S>']:
            with self.subTest(linha=linha):
                g = construir_grafo_posicoes([linha])
                self.assertEqual(g.vizinhos((0, linha.index('>'))), [])

    def test_esteira_apontando_para_porta(self):
        self.assertEqual(construir_grafo_posicoes(['S>AG']).vizinhos((0, 1)),
                         [((0, 2), 1)])
        self.assertEqual(construir_grafo_posicoes(['S>AG'], 'parede').vizinhos((0, 1)), [])

    def test_multiplas_saidas_terminais(self):
        g = construir_grafo_posicoes(['GSG'])
        self.assertEqual(g.vizinhos((0, 0)), [])
        self.assertEqual(g.vizinhos((0, 2)), [])
        self.assertEqual(g.vizinhos((0, 1)), [((0, 2), 1), ((0, 0), 1)])

    def test_modo_invalido_e_matriz_preservada(self):
        matriz = [list('SA+G')]
        original = [linha[:] for linha in matriz]
        with self.assertRaises(ValueError):
            construir_grafo_posicoes(matriz, 'outro')
        construir_grafo_posicoes(matriz)
        construir_grafo_posicoes(matriz, 'parede')
        self.assertEqual(matriz, original)

    def test_oito_mapas_nos_dois_modos(self):
        caminhos = sorted((Path(__file__).resolve().parents[1] / 'data/mapas').glob('*.txt'))
        self.assertEqual(len(caminhos), 8)
        for caminho in caminhos:
            matriz, _, _ = ler_mapa(caminho)
            for modo in ['chao', 'parede']:
                with self.subTest(mapa=caminho.name, portas=modo):
                    g = construir_grafo_posicoes(matriz, modo)
                    esperados = [(i, j) for i, linha in enumerate(matriz)
                                 for j, simbolo in enumerate(linha)
                                 if simbolo != '#' and not (modo == 'parede' and simbolo in 'ABCD')]
                    self.assertEqual(g.vertices, esperados)
                    vertices = set(g.vertices)
                    for u, v, _ in g.arestas:
                        self.assertIn(u, vertices)
                        self.assertIn(v, vertices)
                        self.assertEqual(abs(u[0]-v[0]) + abs(u[1]-v[1]), 1)
