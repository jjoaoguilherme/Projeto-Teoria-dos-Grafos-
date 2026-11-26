"""[IA] ChatGPT – testes da integração da CLI e dos registros de busca."""
import csv
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from src.graphs.graph import Grafo
from src.parte2.cli import consultar, executar_benchmark
from src.parte2.experimentos import carregar_grafo_experimento, verificar_casos_bellman_ford
from src.parte2.verificar_experimentos import verificar_pasta


class TestCLIParte2(unittest.TestCase):
    def test_ordem_camadas_ciclo(self):
        grafo = Grafo(['A', 'B', 'C', 'D', 'E'],
                      [('A', 'C', 1), ('A', 'B', 1), ('C', 'D', 1), ('D', 'A', -1)])
        bfs = consultar(grafo, 'BFS', 'A')
        self.assertEqual(bfs['ordem_visita'], ['A', 'C', 'B', 'D'])
        self.assertEqual(bfs['camadas'], {'0': ['A'], '1': ['C', 'B'], '2': ['D']})
        dfs = consultar(grafo, 'DFS', 'A')
        self.assertEqual(dfs['ordem_visita'], ['A', 'C', 'D', 'B'])
        self.assertTrue(dfs['tem_ciclo'])
        self.assertIsNone(bfs['distancias']['E'])

    def test_cli_dijkstra(self):
        with TemporaryDirectory() as pasta:
            pasta = Path(pasta)
            csv_path = pasta / 'arcos.csv'
            csv_path.write_text('origem,destino,peso\nA,B,-1\nA,C,1\nC,B,1\n', encoding='utf-8')
            subprocess.run([sys.executable, '-m', 'src.cli', '--dataset', str(csv_path),
                            '--alg', 'DIJKSTRA', '--source', 'A', '--target', 'B',
                            '--out', str(pasta)], capture_output=True, check=True)
            dados = json.loads((pasta / 'consulta_dijkstra.json').read_text(encoding='utf-8'))
            self.assertEqual(dados['custo'], 2)
            self.assertEqual(dados['caminho'], ['A', 'C', 'B'])

    def test_procedencia_recusa_base_sem_arcos(self):
        with self.assertRaisesRegex(ValueError, 'não contém todos'):
            verificar_casos_bellman_ford(Grafo(['A'], []), 'inexistente.csv')

    def test_benchmark_completo(self):
        with TemporaryDirectory() as pasta:
            pasta = Path(pasta)
            arquivo = pasta / 'arcos.csv'
            arcos = [('xboxone', 'battlefield_4', 1), ('fitnesscirclejerk', 'leangains', 1),
                     ('jleague', 'soccer', 1), ('bestof', 'confession', 1),
                     ('subredditdrama', 'nfl', -1), ('2007scape', 'runescape', -1),
                     ('runescape', '2007scape', -1), ('titlegore', 'bestof', 1)]
            with arquivo.open('w', encoding='utf-8', newline='') as f:
                w = csv.writer(f)
                w.writerow(['origem', 'destino', 'peso'])
                w.writerows(arcos)
            destino = executar_benchmark(arquivo, carregar_grafo_experimento(arquivo),
                                         pasta, limite_vertices=12)
            dados = json.loads(destino.read_text(encoding='utf-8'))
            self.assertEqual(len(dados['experimentos']), 25)
            verificacao = verificar_pasta(pasta)
            self.assertTrue(verificacao['medicoes_validas'])
            self.assertTrue(verificacao['consolidado_consistente'])
