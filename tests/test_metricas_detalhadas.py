"""Contas manuais e invariantes das métricas por estado, casa e camada."""
from pathlib import Path
from collections import Counter
import csv
import json
import tempfile
import unittest

from src.graphs.estados import construir_grafo_estados
from src.graphs.graph import Grafo
from src.graphs.io import ler_mapa
from src.graphs.metricas import calcular_pacote_metricas, exportar_pacotes_metricas


def pacote(linhas, inicio=(0, 0), nome='teste', modo=False):
    matriz = [list(l) for l in linhas]
    return calcular_pacote_metricas(matriz, construir_grafo_estados(matriz, inicio, modo), nome, modo)


class TestMetricasDetalhadas(unittest.TestCase):
    def test_graus_rankings_e_multiplicidade_contados_a_mao(self):
        p = pacote(['SaG'])
        graus = {g['estado']: (g['grau_entrada'], g['grau_saida']) for g in p['graus']}
        self.assertEqual(graus, {'(0,0)|-|{}': (0, 1), '(0,0)|a|{}': (1, 1),
                                 '(0,1)|a|{}': (2, 2), '(0,2)|a|{}': (1, 0)})
        m = p['globais']
        self.assertEqual(m['rankings']['maior_grau_entrada'], {'estado': '(0,1)|a|{}', 'grau': 2})
        self.assertEqual(m['rankings']['maior_grau_saida'], {'estado': '(0,1)|a|{}', 'grau': 2})
        self.assertEqual(m['becos']['quantidade'], 0)
        self.assertEqual(m['multiplicidade']['maxima'], 2)
        self.assertEqual(m['multiplicidade']['casas_maximas'], [[0, 0]])

    def test_camadas_sao_induzidas_e_coleta_muda_camada(self):
        c = pacote(['SaG'])['camadas']
        self.assertEqual(c['camadas'], {'-': {'ordem': 1, 'tamanho': 0, 'densidade': 0},
                                       'a': {'ordem': 3, 'tamanho': 3, 'densidade': 0.5}})
        self.assertEqual(c['arcos_entre_camadas'], {
            'quantidade': 1, 'transicoes': [{'origem': '-', 'destino': 'a', 'quantidade': 1}],
            'por_casa': [{'posicao': [0, 1], 'chave': 'a', 'quantidade': 1}]})

    def test_bonus_nao_cria_camada_de_chaves(self):
        p = pacote(['S+G'])
        self.assertEqual(p['camadas']['camadas'],
                         {'-': {'ordem': 4, 'tamanho': 4, 'densidade': 4 / 12}})
        self.assertEqual(p['camadas']['arcos_entre_camadas']['quantidade'], 0)

    def test_becos_excluem_saidas_e_alvo(self):
        p = pacote(['S>#G'])
        self.assertEqual(p['globais']['becos'], {'quantidade': 1, 'estados': ['(0,1)|-|{}']})
        self.assertNotIn('ALVO', [r['estado'] for r in p['graus']])
        self.assertEqual(p['globais']['multiplicidade']['por_casa'][-1],
                         {'posicao': [0, 3], 'multiplicidade': 0})

    def test_multiplas_saidas_nao_inflam_graus(self):
        p = pacote(['GSG'], inicio=(0, 1))
        self.assertEqual(sum(g['grau_saida'] for g in p['graus']), 2)
        self.assertEqual(p['globais']['becos']['quantidade'], 0)

    def test_empate_usa_rotulo_lexicografico_independente_da_insercao(self):
        from src.graphs.metricas import calcular_detalhes_estados
        dados = {'grafo': Grafo(['z', 'a', 'ALVO']),
                 'estados': {'z': ((0, 0), frozenset(), frozenset()),
                             'a': ((0, 1), frozenset(), frozenset())}}
        d = calcular_detalhes_estados(['SG'], dados)
        self.assertEqual(d['rankings']['maior_grau_saida'], {'estado': 'a', 'grau': 0})
        self.assertEqual(d['rankings']['maior_grau_entrada'], {'estado': 'a', 'grau': 0})

    def test_exporta_csv_e_preserva_outros_mapas_e_variantes(self):
        pacotes = [pacote(['S.G'], nome='a'), pacote(['S*G'], nome='a', modo=True),
                   pacote(['S#G'], nome='b')]
        with tempfile.TemporaryDirectory() as pasta:
            for p in pacotes: exportar_pacotes_metricas([p], pasta)
            exportar_pacotes_metricas([pacotes[0]], pasta)
            c = json.loads((Path(pasta) / 'camadas.json').read_text(encoding='utf-8'))
            self.assertEqual(set(c), {'a', 'a_fonte_consumivel', 'b'})
            for p, nome in zip(pacotes, ['a', 'a_fonte_consumivel', 'b']):
                with (Path(pasta) / ('graus_' + nome + '.csv')).open(encoding='utf-8', newline='') as f:
                    linhas = list(csv.DictReader(f))
                self.assertEqual(len(linhas), p['globais']['G_est']['ordem'])
                self.assertEqual(list(linhas[0]), ['estado', 'grau_entrada', 'grau_saida'])

    def test_camadas_invalidas_nao_sao_sobrescritas(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / 'camadas.json'
            arquivo.write_text('[]', encoding='utf-8')
            with self.assertRaises(ValueError): exportar_pacotes_metricas([pacote(['SG'])], pasta)
            self.assertEqual(arquivo.read_text(encoding='utf-8'), '[]')

    def test_invariantes_todos_os_mapas_e_fonte_consumivel(self):
        raiz = Path(__file__).resolve().parents[1]
        caminhos = sorted((raiz / 'data/mapas').glob('*.txt')) + sorted((raiz / 'data/mapas_grupo').glob('*.txt'))
        casos = [(p, False) for p in caminhos] + [(raiz / 'data/mapas/m06_fonte.txt', True)]
        for caminho, modo in casos:
            with self.subTest(mapa=caminho.name, modo=modo):
                matriz, inicio, _ = ler_mapa(caminho)
                dados = construir_grafo_estados(matriz, inicio, modo)
                p = calcular_pacote_metricas(matriz, dados, caminho.stem, modo)
                m, c = p['globais'], p['camadas']
                self.assertEqual(sum(g['grau_entrada'] for g in p['graus']), m['G_est']['tamanho'])
                self.assertEqual(sum(g['grau_saida'] for g in p['graus']), m['G_est']['tamanho'])
                self.assertEqual(sum(x['ordem'] for x in c['camadas'].values()), m['G_est']['ordem'])
                self.assertEqual(sum(x['tamanho'] for x in c['camadas'].values()) + c['arcos_entre_camadas']['quantidade'], m['G_est']['tamanho'])
                esperado = Counter(e[0] for e in dados['estados'].values())
                for casa in m['multiplicidade']['por_casa']:
                    self.assertEqual(casa['multiplicidade'], esperado[tuple(casa['posicao'])])
                self.assertEqual(sum(x['multiplicidade'] for x in m['multiplicidade']['por_casa']), m['G_est']['ordem'])
                self.assertTrue(all(x['chave'] in 'abcd' for x in c['arcos_entre_camadas']['por_casa']))
