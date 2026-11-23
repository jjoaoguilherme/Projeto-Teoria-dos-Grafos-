"""[IA] Codex – testes da infraestrutura, sem limites de velocidade da máquina."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
from src.parte2.experimentos import medir_algoritmo, exportar_relatorio, registrar_ambiente


class TestExperimentos(unittest.TestCase):
    def test_cinco_chamadas_media_e_retorno(self):
        algoritmo = Mock(return_value={'tem_ciclo_negativo': False})
        with patch('src.parte2.experimentos.time.perf_counter',
                   side_effect=[0, 1, 2, 4, 5, 8, 9, 13, 14, 19]):
            r = medir_algoritmo(algoritmo, ['A'], [], 'A')
        self.assertEqual(algoritmo.call_count, 5)
        self.assertEqual(r['tempos_segundos'], [1, 2, 3, 4, 5])
        self.assertEqual(r['tempo_medio_segundos'], 3)
        self.assertEqual(r['status_execucoes'], ['OK'] * 5)

    def test_repeticoes_invalidas_nao_executam(self):
        algoritmo = Mock()
        for valor in [0, 4, -1, 5.5, True, '5']:
            with self.subTest(valor=valor), self.assertRaises(ValueError):
                medir_algoritmo(algoritmo, [], [], 'A', valor)
        algoritmo.assert_not_called()

    def test_quatro_algoritmos_preservam_entrada_e_aceitam_geradores(self):
        vertices = ['A', 'B', 'C']
        arestas = [('A', 'B', 2), ('B', 'C', 1)]
        for nome in ['BFS', 'DFS', 'DIJKSTRA', 'BELLMAN_FORD']:
            r = medir_algoritmo(nome, iter(vertices), iter(arestas), 'A', 6)
            self.assertEqual(r['repeticoes'], 6)
            self.assertEqual(len(r['tempos_segundos']), 6)
            self.assertEqual((r['vertices'], r['arestas']), (3, 2))
        self.assertEqual(vertices, ['A', 'B', 'C'])
        self.assertEqual(arestas, [('A', 'B', 2), ('B', 'C', 1)])

    def test_ciclo_negativo_e_recusa_nao_ocultada(self):
        r = medir_algoritmo('BELLMAN_FORD', ['A'], [('A', 'A', -1)], 'A')
        self.assertEqual(r['status_execucoes'], ['CICLO_NEGATIVO'] * 5)
        with self.assertRaisesRegex(ValueError, 'negativos'):
            medir_algoritmo('DIJKSTRA', ['A'], [('A', 'A', -1)], 'A')

    def test_exportacao_e_ambiente(self):
        ambiente = registrar_ambiente()
        self.assertIn('python', ambiente)
        self.assertEqual(ambiente['relogio'], 'time.perf_counter')
        with tempfile.TemporaryDirectory() as pasta:
            destino = exportar_relatorio([{'teste': 1}], Path(pasta) / 'sub/report.json',
                                         ambiente=ambiente, demonstracao=True)
            dados = json.loads(destino.read_text(encoding='utf-8'))
        self.assertTrue(dados['demonstracao'])
        self.assertEqual(dados['experimentos'], [{'teste': 1}])
        self.assertEqual(dados['ambiente'], ambiente)

    def test_json_invalido_preserva_arquivo(self):
        with tempfile.TemporaryDirectory() as pasta:
            destino = Path(pasta) / 'report.json'
            destino.write_text('original', encoding='utf-8')
            with self.assertRaises(ValueError):
                exportar_relatorio([{'tempo': float('nan')}], destino, ambiente={})
            self.assertEqual(destino.read_text(), 'original')
