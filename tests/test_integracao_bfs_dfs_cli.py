"""[IA] ChatGPT – testes do executor de medição, não de algoritmos."""
import csv
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.parte2.experimentos import executar_bfs_dfs_dataset


class TestIntegracaoBfsDfs(unittest.TestCase):
    def test_relatorio_seis_medicoes(self):
        with TemporaryDirectory() as temp:
            arquivo = Path(temp) / 'mini.tsv'
            with arquivo.open('w', encoding='utf-8', newline='') as f:
                w = csv.writer(f, delimiter='\t')
                w.writerow(['SOURCE_SUBREDDIT', 'TARGET_SUBREDDIT', 'LINK_SENTIMENT'])
                w.writerows([('A', 'B', '1'), ('B', 'C', '-1'), ('C', 'A', '1')])
            destino = Path(temp) / 'resultado.json'
            caminho = executar_bfs_dfs_dataset(arquivo, ['A', 'B', 'C'], 5, destino)
            dados = json.loads(caminho.read_text(encoding='utf-8'))
            self.assertFalse(dados['demonstracao'])
            self.assertEqual(len(dados['experimentos']), 6)
            self.assertEqual({e['algoritmo'] for e in dados['experimentos']}, {'BFS', 'DFS'})
            self.assertEqual({e['origem'] for e in dados['experimentos']}, {'A', 'B', 'C'})
            self.assertTrue(all(e['repeticoes'] == 5 for e in dados['experimentos']))

    def test_fonte_ausente_nao_gera_arquivo(self):
        with TemporaryDirectory() as temp:
            arquivo = Path(temp) / 'mini.tsv'
            arquivo.write_text('SOURCE_SUBREDDIT\tTARGET_SUBREDDIT\tLINK_SENTIMENT\nA\tB\t1\n', encoding='utf-8')
            destino = Path(temp) / 'resultado.json'
            with self.assertRaisesRegex(ValueError, 'Fontes não encontradas'):
                executar_bfs_dfs_dataset(arquivo, ['A', 'B', 'Z'], 5, destino)
            self.assertFalse(destino.exists())
