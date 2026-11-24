"""[IA] Codex – conferência numérica das fórmulas e razões exportadas."""
import csv
import json
from pathlib import Path
import tempfile
import unittest
from test_graficos_escalabilidade import dados_simulados
from src.parte2.tabela_complexidades import gerar_tabela


class TestTabelaComplexidades(unittest.TestCase):
    def test_formulas_e_razoes(self):
        with tempfile.TemporaryDirectory() as pasta:
            entrada = Path(pasta) / 'report.json'
            entrada.write_text(json.dumps(dados_simulados()), encoding='utf-8')
            saida = gerar_tabela(entrada, Path(pasta) / 'tabela.csv')
            with saida.open(encoding='utf-8', newline='') as arquivo:
                linhas = list(csv.DictReader(arquivo))
        self.assertEqual(len(linhas), 12)
        for nome in ('BFS', 'DFS', 'DIJKSTRA', 'BELLMAN_FORD'):
            primeira = next(l for l in linhas if l['algoritmo'] == nome)
            self.assertEqual(float(primeira['tempo_relativo']), 1)
            self.assertEqual(float(primeira['fator_relativo']), 1)
        self.assertEqual(float(linhas[0]['fator_referencia']), 19)
        bf = next(l for l in linhas if l['algoritmo'] == 'BELLMAN_FORD')
        self.assertEqual(float(bf['fator_referencia']), 109)
