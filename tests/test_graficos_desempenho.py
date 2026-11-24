"""[IA] Codex – dados e exportação das figuras de desempenho."""
import importlib
import json
from pathlib import Path
import tempfile
import unittest

visualizacoes = importlib.import_module('src.parte2.visualizações')


class TestGraficosDesempenho(unittest.TestCase):
    def dados(self):
        return {'demonstracao': False, 'experimentos': [{
            'algoritmo': 'BFS', 'tarefa': 'busca', 'origem': 'A',
            'vertices': 3, 'arestas': 2, 'repeticoes': 5, 'unidade': 'segundos',
            'tempos_segundos': [1, 2, 3, 4, 5], 'tempo_medio_segundos': 3,
            'status_execucoes': ['OK'] * 5}]}

    def test_media_desvio_e_preservacao(self):
        dados = self.dados()
        antes = json.dumps(dados)
        serie = visualizacoes.preparar_series(dados)[(3, 2)][0]
        self.assertEqual(serie['media'], 3)
        self.assertAlmostEqual(serie['desvio'], (2.5)**.5)
        self.assertEqual(json.dumps(dados), antes)

    def test_separa_grafos_de_tamanhos_distintos(self):
        dados = self.dados()
        outro = dict(dados['experimentos'][0], vertices=2, arestas=1)
        dados['experimentos'].append(outro)
        self.assertEqual(len(visualizacoes.preparar_series(dados)), 2)

    def test_recusa_media_incorreta(self):
        dados = self.dados()
        dados['experimentos'][0]['tempo_medio_segundos'] = 99
        with self.assertRaises(ValueError):
            visualizacoes.preparar_series(dados)

    def test_exporta_png_e_svg(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / 'report.json'
            arquivo.write_text(json.dumps(self.dados()), encoding='utf-8')
            saidas = visualizacoes.gerar_graficos(arquivo, Path(pasta) / 'figuras')
            self.assertEqual({p.suffix for p in saidas}, {'.png', '.svg'})
            self.assertTrue(all(p.stat().st_size > 100 for p in saidas))
