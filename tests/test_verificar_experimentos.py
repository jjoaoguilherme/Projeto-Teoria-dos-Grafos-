"""[IA] Codex – testes da verificação de relatórios de medição."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from src.parte2.verificar_experimentos import verificar_relatorio, verificar_pasta


class TestVerificacaoExperimentos(unittest.TestCase):
    def setUp(self):
        self.relatorio = {'demonstracao': False, 'experimentos': [{
            'algoritmo': 'BFS', 'vertices': 3, 'arestas': 2, 'repeticoes': 5,
            'unidade': 'segundos', 'tempos_segundos': [1, 2, 3, 4, 5],
            'tempo_medio_segundos': 3, 'status_execucoes': ['OK'] * 5}]}

    def test_relatorio_valido(self):
        antes = deepcopy(self.relatorio)
        self.assertTrue(verificar_relatorio(self.relatorio)['valido'])
        self.assertEqual(self.relatorio, antes)

    def test_erros_numericos_e_status(self):
        for campo, valor in [('repeticoes', 4), ('vertices', True), ('arestas', -1),
                             ('tempo_medio_segundos', 4), ('unidade', 'ms'),
                             ('tempos_segundos', [float('nan')] * 5),
                             ('tempos_segundos', [-1] * 5), ('status_execucoes', ['OK']),
                             ('algoritmo', 'inexistente')]:
            with self.subTest(campo=campo, valor=valor):
                r = deepcopy(self.relatorio)
                r['experimentos'][0][campo] = valor
                self.assertFalse(verificar_relatorio(r)['valido'])

    def test_estrutura_invalida_e_demonstracao(self):
        for r in [None, {}, {'experimentos': []}, {'experimentos': [None]},
                  dict(self.relatorio, demonstracao=True)]:
            self.assertFalse(verificar_relatorio(r)['valido'])

    def test_consolidacao_confere_multiplicidade(self):
        with tempfile.TemporaryDirectory() as pasta:
            for nome in ['bfs_dfs', 'dijkstra', 'bellman_ford']:
                (Path(pasta) / (nome + '_report.json')).write_text(json.dumps(self.relatorio))
            consolidado = deepcopy(self.relatorio)
            consolidado['experimentos'] *= 3
            arquivo = Path(pasta) / 'parte2_report.json'
            arquivo.write_text(json.dumps(consolidado))
            self.assertTrue(verificar_pasta(pasta)['consolidado_consistente'])
            consolidado['experimentos'].pop()
            arquivo.write_text(json.dumps(consolidado))
            self.assertFalse(verificar_pasta(pasta)['consolidado_consistente'])

    def test_arquivos_ausentes(self):
        with tempfile.TemporaryDirectory() as pasta:
            self.assertFalse(verificar_pasta(pasta)['medicoes_validas'])
