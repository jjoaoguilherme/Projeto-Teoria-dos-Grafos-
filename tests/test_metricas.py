"""Conferência manual das fórmulas, exclusão de ALVO e exportação pela CLI."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from src.graphs.graph import Grafo
from src.graphs.metricas import (
    calcular_metricas_grafo, calcular_metricas_mapa, calcular_metricas_percurso,
    exportar_metricas_globais,
)

RAIZ = Path(__file__).resolve().parents[1]


class TestMetricas(unittest.TestCase):
    def mapa(self, texto, fonte_consumivel=False):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / 'teste.txt'
            caminho.write_text(texto, encoding='utf-8')
            return calcular_metricas_mapa(caminho, fonte_consumivel)

    def test_direcoes_e_densidade_contadas_a_mao(self):
        g = Grafo('ABC', [('A', 'B', 1), ('B', 'A', 7), ('B', 'C', -4)])
        self.assertEqual(calcular_metricas_grafo(g),
                         {'ordem': 3, 'tamanho': 3, 'densidade': 0.5})

    def test_vazio_unitario_e_vertice_isolado(self):
        for vertices, ordem in [([], 0), (['A'], 1), (['A', 'B'], 2)]:
            with self.subTest(vertices=vertices):
                self.assertEqual(calcular_metricas_grafo(Grafo(vertices)),
                                 {'ordem': ordem, 'tamanho': 0, 'densidade': 0.0})

    def test_exclui_alvo_e_arcos_em_ambas_direcoes_sem_mutar(self):
        g = Grafo(['A', 'B', 'C', 'ALVO'], [('A', 'B', 1), ('B', 'A', 1),
                  ('B', 'C', 1), ('C', 'ALVO', 0), ('ALVO', 'A', 0)])
        antes = (g.vertices, g.arestas)
        self.assertEqual(calcular_metricas_grafo(g, {'ALVO'}),
                         {'ordem': 3, 'tamanho': 3, 'densidade': 0.5})
        self.assertEqual((g.vertices, g.arestas), antes)

    def test_mapa_sem_inventario_contado_a_mao(self):
        m = self.mapa('S.G')
        for chave in ['G_pos', 'G_est']:
            self.assertEqual(m[chave], {'ordem': 3, 'tamanho': 3, 'densidade': 0.5})
        self.assertEqual(m['casas_livres'], 3)
        self.assertEqual(m['teto_teorico'], 3)
        self.assertEqual(m['taxa_ocupacao'], 1)

    def test_chave_cria_estados_diferentes_na_mesma_casa(self):
        m = self.mapa('SaG')
        self.assertEqual(m['G_pos']['ordem'], 3)
        self.assertEqual(m['G_est']['ordem'], 4)
        self.assertEqual(m['G_est']['tamanho'], 4)
        self.assertEqual(m['teto_teorico'], 6)
        self.assertAlmostEqual(m['taxa_ocupacao'], 4 / 6)
        self.assertAlmostEqual(m['G_est']['densidade'], 4 / 12)

    def test_bonus_aumenta_teto_e_estado(self):
        m = self.mapa('S+G')
        self.assertEqual(m['numero_bonus'], 1)
        self.assertEqual(m['numero_chaves'], 0)
        self.assertEqual(m['teto_teorico'], 6)
        self.assertEqual(m['G_est']['ordem'], 4)
        self.assertEqual(m['G_est']['tamanho'], 4)

    def test_chaves_repetidas_contam_um_tipo_e_bonus_sao_individuais(self):
        m = self.mapa('Saa++G')
        self.assertEqual(m['chaves'], ['a'])
        self.assertEqual(m['numero_chaves'], 1)
        self.assertEqual(m['numero_bonus'], 2)
        self.assertEqual(m['teto_teorico'], 6 * 2 * 4)

    def test_casas_inalcancaveis_entram_no_teto_e_gpos(self):
        m = self.mapa('S#a+G')
        self.assertEqual(m['casas_livres'], 4)
        self.assertEqual(m['G_pos']['ordem'], 4)
        self.assertEqual(m['G_est'], {'ordem': 1, 'tamanho': 0, 'densidade': 0.0})
        self.assertEqual(m['teto_teorico'], 16)
        self.assertEqual(m['taxa_ocupacao'], 1 / 16)

    def test_portas_entram_nas_casas_livres_do_gpos(self):
        m = self.mapa('SAG')
        self.assertEqual(m['G_pos']['ordem'], 3)
        self.assertEqual(m['G_pos']['tamanho'], 3)
        self.assertEqual(m['G_est']['ordem'], 1)
        self.assertEqual(m['numero_chaves'], 0)

    def test_todas_as_ligacoes_de_saida_ao_alvo_sao_excluidas(self):
        m = self.mapa('GSG')
        self.assertEqual(m['G_est'], {'ordem': 3, 'tamanho': 2, 'densidade': 2 / 6})

    def test_fonte_consumivel_acrescenta_bit_apenas_na_variante(self):
        normal = self.mapa('S*G')
        consumivel = self.mapa('S*G', True)
        self.assertEqual(normal['numero_fontes_consumiveis'], 0)
        self.assertEqual(normal['teto_teorico'], 3)
        self.assertEqual(consumivel['numero_fontes_consumiveis'], 1)
        self.assertEqual(consumivel['numero_bonus'], 0)
        self.assertEqual(consumivel['teto_teorico'], 6)
        self.assertEqual(consumivel['G_est']['ordem'], 4)
        self.assertEqual(normal['G_pos'], consumivel['G_pos'])

    def test_exportacao_preserva_outros_mapas_e_separa_modos(self):
        a = self.mapa('S.G')
        a['mapa'] = 'mapa_a'
        b = self.mapa('S*G', True)
        b['mapa'] = 'mapa_a'
        c = self.mapa('S#G')
        c['mapa'] = 'mapa_c'
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = exportar_metricas_globais([a, c], pasta)
            exportar_metricas_globais([b], pasta)
            exportar_metricas_globais([a], pasta)
            dados = json.loads(arquivo.read_text(encoding='utf-8'))
            self.assertEqual(dados, {'mapa_a': a, 'mapa_a_fonte_consumivel': b, 'mapa_c': c})

    def test_exportacao_recusa_formato_invalido_sem_apagar(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / 'metricas_global.json'
            for conteudo in ['[]', '{invalido']:
                arquivo.write_text(conteudo, encoding='utf-8')
                with self.assertRaises(ValueError):
                    exportar_metricas_globais([], pasta)
                self.assertEqual(arquivo.read_text(encoding='utf-8'), conteudo)

    def cli(self, *args):
        return subprocess.run([sys.executable, '-X', 'utf8', '-m', 'src.cli', *args], cwd=RAIZ,
                              capture_output=True, text=True, encoding='utf-8')

    def test_cli_um_mapa_sem_gerar_solucoes(self):
        with tempfile.TemporaryDirectory() as pasta:
            r = self.cli('--metricas', '--mapa', 'data/mapas/m02_uma_chave.txt', '--out', pasta)
            self.assertEqual(r.returncode, 0, r.stderr)
            dados = json.loads((Path(pasta) / 'metricas_global.json').read_text(encoding='utf-8'))
            self.assertEqual(set(dados), {'m02_uma_chave'})
            self.assertEqual(dados['m02_uma_chave']['G_est']['ordem'], 39)
            self.assertEqual([p.name for p in Path(pasta).iterdir()], ['metricas_global.json'])

    def test_cli_todos_os_mapas(self):
        esperados = {p.stem for pasta in ['mapas', 'mapas_grupo']
                     for p in (RAIZ / 'data' / pasta).glob('*.txt')}
        with tempfile.TemporaryDirectory() as pasta:
            r = self.cli('--metricas', '--out', pasta)
            self.assertEqual(r.returncode, 0, r.stderr)
            dados = json.loads((Path(pasta) / 'metricas_global.json').read_text(encoding='utf-8'))
            self.assertEqual(set(dados), esperados)
            for m in dados.values():
                self.assertGreater(m['taxa_ocupacao'], 0)
                self.assertLessEqual(m['taxa_ocupacao'], 1)
                self.assertEqual(m['G_pos']['ordem'], m['casas_livres'])

    def test_cli_opcoes_incompativeis_e_arquivo_invalido(self):
        for args in [('--metricas', '--alg', 'BFS'),
                     ('--metricas', 'm02_uma_chave'),
                     ('--metricas', '--mapa', 'inexistente.txt')]:
            with self.subTest(args=args):
                self.assertNotEqual(self.cli(*args).returncode, 0)

    def test_cli_fonte_consumivel(self):
        with tempfile.TemporaryDirectory() as pasta:
            r = self.cli('--metricas', '--mapa', 'data/mapas/m06_fonte.txt',
                         '--fonte-consumivel', '--out', pasta)
            self.assertEqual(r.returncode, 0, r.stderr)
            dados = json.loads((Path(pasta) / 'metricas_global.json').read_text(encoding='utf-8'))
            self.assertTrue(dados['m06_fonte_fonte_consumivel']['fonte_consumivel'])


class TestMetricasCompartilhadas(unittest.TestCase):
    def test_percurso_vazio_sem_metricas_inventadas(self):
        self.assertEqual(calcular_metricas_percurso([]), {
            'passos': None, 'custo': None,
            'custo_medio_por_movimento': None, 'casas_distintas': None,
        })

    def test_percurso_sem_movimentos(self):
        self.assertEqual(calcular_metricas_percurso([
            {'posicao': [0, 0], 'custo_acumulado': 0}
        ]), {'passos': 0, 'custo': 0, 'custo_medio_por_movimento': None,
             'casas_distintas': 1})

    def test_casas_repetidas_e_media(self):
        percurso = [{'posicao': [0, 0], 'custo_acumulado': 0},
                    {'posicao': [0, 1], 'custo_acumulado': 3},
                    {'posicao': [0, 0], 'custo_acumulado': 4},
                    {'posicao': [0, 2], 'custo_acumulado': 8}]
        self.assertEqual(calcular_metricas_percurso(percurso), {
            'passos': 3, 'custo': 8, 'custo_medio_por_movimento': 8 / 3,
            'casas_distintas': 3,
        })

    def test_media_preserva_custo_negativo(self):
        m = calcular_metricas_percurso([
            {'posicao': [0, 0], 'custo_acumulado': 0},
            {'posicao': [0, 1], 'custo_acumulado': -4},
            {'posicao': [0, 2], 'custo_acumulado': -3},
        ])
        self.assertEqual(m['custo'], -3)
        self.assertEqual(m['custo_medio_por_movimento'], -1.5)

    def test_resolucao_reutiliza_estados_sem_reconstruir(self):
        from src.main import resolver_mapa
        from src.graphs.estados import construir_grafo_estados, construir_grafo_posicoes
        with patch('src.main.construir_grafo_estados', wraps=construir_grafo_estados) as estados, \
             patch('src.graphs.metricas.construir_grafo_estados') as repetido, \
             patch('src.graphs.metricas.construir_grafo_posicoes', wraps=construir_grafo_posicoes) as posicoes:
            r, _ = resolver_mapa(RAIZ / 'data/mapas/m02_uma_chave.txt')
        estados.assert_called_once()
        repetido.assert_not_called()
        posicoes.assert_called_once()
        self.assertEqual(r['estados_alcancaveis'], r['metricas_globais']['G_est']['ordem'])

    def test_algoritmos_compartilham_metricas_globais_e_campos_legados(self):
        from src.main import resolver_mapa
        caminho = RAIZ / 'data/mapas/m01_terreno.txt'
        esperado = calcular_metricas_mapa(caminho)
        for algoritmo in ['BFS', 'DFS', 'DIJKSTRA', 'BELLMAN_FORD']:
            with self.subTest(algoritmo=algoritmo):
                r, _ = resolver_mapa(caminho, algoritmo=algoritmo)
                self.assertEqual(r['metricas_globais'], esperado)
                self.assertEqual(r['passos'], r['metricas_percurso']['passos'])
                self.assertEqual(r['custo'], r['metricas_percurso']['custo'])

    def test_exportacao_usa_mesmo_objeto_de_metricas(self):
        from src.main import resolver_mapa, exportar_resultado
        with tempfile.TemporaryDirectory() as pasta:
            r, g = resolver_mapa(RAIZ / 'data/mapas/m02_uma_chave.txt')
            exportar_resultado(r, g, pasta)
            global_json = json.loads((Path(pasta) / 'metricas_global.json').read_text(encoding='utf-8'))
            resultado = json.loads((Path(pasta) / 'resultado_m02_uma_chave.json').read_text(encoding='utf-8'))
            self.assertEqual(resultado['metricas_globais'], global_json['m02_uma_chave'])
            self.assertEqual(resultado['metricas_percurso'], calcular_metricas_percurso(resultado['percurso']))

    def test_recusa_e_sem_solucao_sem_indicadores_de_percurso(self):
        from src.main import resolver_mapa
        for nome, algoritmo, status in [('m05_bonus', 'DIJKSTRA', 'RECUSA'),
                                        ('m07_impossivel', 'BFS', 'SEM_SOLUCAO'),
                                        ('m06_fonte', 'BELLMAN_FORD', 'CICLO_NEGATIVO')]:
            with self.subTest(nome=nome):
                r, _ = resolver_mapa(RAIZ / 'data/mapas' / (nome + '.txt'), algoritmo=algoritmo)
                self.assertEqual(r['status'], status)
                self.assertEqual(r['metricas_percurso'], calcular_metricas_percurso([]))
                self.assertGreater(r['metricas_globais']['G_est']['ordem'], 0)
