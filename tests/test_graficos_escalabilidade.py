"""[IA] Codex – validação de séries e figuras usando tempos simulados."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from src.parte2.experimentos import ALGORITMOS
from src.parte2.graficos_escalabilidade import preparar_escalabilidade, gerar_graficos


def dados_simulados():
    return {'demonstracao': False, 'experimentos': [
        {'algoritmo': nome, 'origem': 'A', 'vertices': n, 'arestas': n-1,
         'repeticoes': 5, 'unidade': 'segundos', 'tempos_segundos': [n/1000] * 5,
         'tempo_medio_segundos': n/1000, 'status_execucoes': ['OK'] * 5,
         'identificacao': {'caso': 'ESCALABILIDADE', 'amostragem': {
             'vertices': n, 'arestas': n-1, 'semente': 42,
             'vertices_selecionados': list(range(n))}}}
        for nome in ALGORITMOS for n in (10, 50, 100)]}


class TestGraficosEscalabilidade(unittest.TestCase):
    def test_ordena_sem_modificar(self):
        dados = dados_simulados()
        dados['experimentos'].reverse()
        antes = deepcopy(dados)
        series = preparar_escalabilidade(dados)
        self.assertEqual(set(series), set(ALGORITMOS))
        self.assertTrue(all([e['vertices'] for e in s] == [10, 50, 100] for s in series.values()))
        self.assertEqual(dados, antes)

    def test_rejeita_tamanhos_faltantes_duplicatas_e_misturas(self):
        for alteracao in ('falta', 'duplicata', 'origem', 'semente', 'amostra', 'caso'):
            with self.subTest(alteracao=alteracao):
                dados = dados_simulados()
                item = dados['experimentos'][0]
                if alteracao == 'falta':
                    dados['experimentos'].pop()
                elif alteracao == 'duplicata':
                    dados['experimentos'].append(deepcopy(item))
                elif alteracao == 'origem':
                    item['origem'] = 'B'
                elif alteracao == 'semente':
                    item['identificacao']['amostragem']['semente'] = 7
                elif alteracao == 'amostra':
                    item['identificacao']['amostragem']['vertices_selecionados'] = ['B']
                else:
                    item['identificacao']['caso'] = 'OUTRO'
                with self.assertRaises(ValueError):
                    preparar_escalabilidade(dados)

    def test_exporta_apenas_em_pasta_temporaria(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / 'simulado.json'
            arquivo.write_text(json.dumps(dados_simulados()), encoding='utf-8')
            saidas = gerar_graficos(arquivo, pasta)
            self.assertEqual({p.suffix for p in saidas}, {'.png', '.svg'})
            self.assertTrue(all(p.stat().st_size > 100 for p in saidas))
