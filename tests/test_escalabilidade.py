"""[IA] Codex – integração da amostragem com medição dos quatro algoritmos."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from src.graphs.graph import Grafo
from src.parte2.escalabilidade import medir_escalabilidade, carregar_arestas_preparadas


class TestEscalabilidade(unittest.TestCase):
    def setUp(self):
        self.grafo = Grafo(range(20), [(i, i+1, 1) for i in range(19)])

    def test_doze_medicoes_com_mesmas_amostras_e_metadados(self):
        resultados = medir_escalabilidade(self.grafo, 0, [.1, .5, 1])
        self.assertEqual(len(resultados), 12)
        self.assertEqual({r['algoritmo'] for r in resultados},
                         {'BFS', 'DFS', 'DIJKSTRA', 'BELLMAN_FORD'})
        self.assertEqual({r['vertices'] for r in resultados}, {2, 10, 20})
        self.assertTrue(all(r['repeticoes'] == 5 for r in resultados))
        for inicio in range(0, 12, 4):
            grupo = resultados[inicio:inicio+4]
            self.assertTrue(all(r['identificacao']['amostragem'] ==
                                grupo[0]['identificacao']['amostragem'] for r in grupo))

    def test_transformacao_dijkstra_e_preservacao(self):
        grafo = Grafo(range(20), [(0, 1, -1), (1, 2, 1)])
        with patch('src.parte2.escalabilidade.medir_algoritmo', return_value={}) as medir:
            medir_escalabilidade(grafo, 0, [.1, .5, 1])
        chamadas = {c.args[0]: c.args[2] for c in medir.call_args_list[-4:]}
        self.assertEqual(chamadas['DIJKSTRA'], [(0, 1, 3), (1, 2, 1)])
        self.assertEqual(chamadas['BELLMAN_FORD'], grafo.arestas)

    def test_recorte_tem_tamanhos_relativos_ao_limite(self):
        resultados = medir_escalabilidade(self.grafo, 0, [.1, .5, 1], limite_vertices=10)
        self.assertEqual({r['vertices'] for r in resultados}, {1, 5, 10})
        self.assertTrue(all(r['identificacao']['dataset_vertices'] == 20 for r in resultados))
        self.assertEqual(len(self.grafo.vertices), 20)

    def test_rejeita_parametros_antes_de_medir(self):
        with patch('src.parte2.escalabilidade.medir_algoritmo') as medir:
            for argumentos in [dict(proporcoes=[.5, 1]),
                               dict(proporcoes=[.1, .5, 1], repeticoes=4),
                               dict(proporcoes=[.1, .5, 1], limite_vertices=100)]:
                with self.assertRaises(ValueError):
                    medir_escalabilidade(self.grafo, 0, **argumentos)
            medir.assert_not_called()

    def test_cli_csv_pequeno_e_json(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / 'arestas.csv'
            arquivo.write_text('origem,destino,peso\nA,B,-1\nB,C,1\nC,D,1\n', encoding='utf-8')
            destino = Path(pasta) / 'resultado.json'
            comando = [sys.executable, '-X', 'utf8', '-m', 'src.parte2.escalabilidade',
                       '--arquivo', str(arquivo), '--origem', 'A', '--proporcoes', '.1', '.5', '1',
                       '--out', str(destino)]
            resultado = subprocess.run(comando, capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(resultado.returncode, 0, resultado.stderr)
            dados = json.loads(destino.read_text(encoding='utf-8'))
            self.assertEqual(len(dados['experimentos']), 12)
            self.assertEqual(len(dados['experimentos'][0]['identificacao']['sha256']), 64)
            self.assertEqual(carregar_arestas_preparadas(arquivo).arestas[0], ('A', 'B', -1))
