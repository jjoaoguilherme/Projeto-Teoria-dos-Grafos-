"""[IA] Codex – preservação de sessões e rejeição de medições inválidas."""
import json
from pathlib import Path
import tempfile
import unittest

from src.parte2.consolidar import consolidar_relatorios


class TestConsolidar(unittest.TestCase):
    def test_preserva_sessoes_e_nao_duplica_ao_reexecutar(self):
        with tempfile.TemporaryDirectory() as pasta:
            for nome in ['bfs_dfs', 'dijkstra', 'bellman_ford']:
                dados = {'demonstracao': False, 'ambiente': {'commit': nome},
                         'experimentos': [{'algoritmo': 'BFS', 'vertices': 2, 'arestas': 1,
                             'repeticoes': 5, 'unidade': 'segundos', 'tempos_segundos': [1]*5,
                             'tempo_medio_segundos': 1, 'status_execucoes': ['OK']*5}]}
                (Path(pasta) / f'{nome}_report.json').write_text(json.dumps(dados))
            destino = consolidar_relatorios(pasta)
            antes = destino.read_text(encoding='utf-8')
            self.assertEqual(len(json.loads(antes)['experimentos']), 3)
            self.assertEqual([s['inicio_experimentos'] for s in json.loads(antes)['sessoes']], [0, 1, 2])
            consolidar_relatorios(pasta)
            self.assertEqual(destino.read_text(encoding='utf-8'), antes)
            (Path(pasta) / 'dijkstra_report.json').write_text('{}')
            with self.assertRaises(ValueError):
                consolidar_relatorios(pasta)
            self.assertEqual(destino.read_text(encoding='utf-8'), antes)
