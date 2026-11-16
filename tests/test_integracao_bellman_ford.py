"""testes de integração das regras do mapa com Bellman-Ford."""
import csv
import json
from pathlib import Path
import tempfile
import unittest
from src.graphs.estados import construir_grafo_estados, criar_estado, verificar_vizinhos
from src.main import resolver_mapa, exportar_resultado

RAIZ = Path(__file__).resolve().parents[1]


class TestIntegracaoBellmanFord(unittest.TestCase):
    def resolver(self, texto, consumivel=False):
        with tempfile.TemporaryDirectory() as pasta:
            mapa = Path(pasta) / 'teste.txt'
            mapa.write_text(texto, encoding='utf-8')
            return resolver_mapa(mapa, consumivel)

    def test_chave_porta_e_saida_terminal(self):
        r, g = self.resolver('S.aAG')
        self.assertEqual((r['status'], r['passos'], r['custo']), ('OK', 4, 4))
        self.assertIn('(0,2)|a|{}', g['vertices'])
        for u, v, p in g['arestas']:
            if u.startswith('(0,4)'):
                self.assertEqual((v, p), ('ALVO', 0))

    def test_bonus_consumido_nao_gera_ciclo_negativo(self):
        r, g = self.resolver('S+G')
        self.assertEqual(r['custo'], -3)
        self.assertEqual(r['status'], 'OK')
        entradas = [(u, p) for u, v, _, casa, p in g['registros'] if casa == '+']
        self.assertTrue(any(p == -4 for _, p in entradas))
        self.assertTrue(any(p == 1 for _, p in entradas))

    def test_esteira_contra_parede_e_porta_fechada(self):
        matriz = [list('S>#G')]
        estado = criar_estado((0, 1), [], [])
        self.assertEqual(verificar_vizinhos(matriz, estado), [])
        r, _ = self.resolver('S>AG')
        self.assertEqual(r['status'], 'SEM_SOLUCAO')

    def test_multiplas_saidas_comentarios_e_sem_solucao(self):
        r, _ = self.resolver('; comentario\nGSG')
        self.assertEqual(r['custo'], 1)
        r, _ = self.resolver('S#G')
        self.assertEqual(r['status'], 'SEM_SOLUCAO')
        self.assertEqual(r['caminho'], [])

    def test_mapas_fornecidos(self):
        for nome, status in [('m02_uma_chave', 'OK'), ('m05_bonus', 'OK'),
                             ('m06_fonte', 'CICLO_NEGATIVO'), ('m07_impossivel', 'SEM_SOLUCAO')]:
            with self.subTest(mapa=nome):
                r, _ = resolver_mapa(RAIZ / 'data/mapas' / f'{nome}.txt')
                self.assertEqual(r['status'], status)
                if r['ciclo_negativo']:
                    self.assertLess(r['custo_ciclo'], 0)
        r, _ = resolver_mapa(RAIZ / 'data/mapas/m06_fonte.txt', True)
        self.assertEqual(r['status'], 'OK')
        self.assertIsNotNone(r['custo'])

    def test_exportacao_preserva_solucoes_e_separa_modos(self):
        with tempfile.TemporaryDirectory() as pasta:
            mapa = Path(pasta) / 'm06_teste.txt'
            mapa.write_text('S*G', encoding='utf-8')
            for modo in [False, True, True]:
                r, g = resolver_mapa(mapa, modo)
                exportar_resultado(r, g, pasta)
            with (Path(pasta) / 'solucoes.csv').open(encoding='utf-8', newline='') as arquivo:
                self.assertEqual(len(list(csv.DictReader(arquivo))), 2)
            dados = json.loads((Path(pasta) / 'ciclo_negativo_m06.json').read_text(encoding='utf-8'))
            self.assertLess(dados['custo'], 0)
