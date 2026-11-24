"""[IA] Codex – testes da verificação de relatórios de medição."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from src.parte2.verificar_experimentos import verificar_relatorio, verificar_pasta
from src.parte2.verificar_experimentos import main


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

    def escrever_relatorios(self, pasta, escalabilidade):
        for nome in ['bfs_dfs', 'dijkstra', 'bellman_ford']:
            (Path(pasta) / (nome + '_report.json')).write_text(json.dumps(self.relatorio))
        (Path(pasta) / 'escalabilidade_report.json').write_text(json.dumps(escalabilidade))
        consolidado = deepcopy(self.relatorio)
        consolidado['experimentos'] *= 3
        consolidado['experimentos'].extend(escalabilidade['experimentos'])
        (Path(pasta) / 'parte2_report.json').write_text(json.dumps(consolidado))

    def escalabilidade(self):
        itens = []
        for nome in ['BFS', 'DFS', 'DIJKSTRA', 'BELLMAN_FORD']:
            for tamanho in [10, 50, 100]:
                item = deepcopy(self.relatorio['experimentos'][0])
                item.update(algoritmo=nome, vertices=tamanho, arestas=tamanho-1, origem='A')
                item['identificacao'] = {'caso': 'ESCALABILIDADE', 'amostragem': {
                    'vertices': tamanho, 'arestas': tamanho-1, 'semente': 42}}
                itens.append(item)
        return {'demonstracao': False, 'experimentos': itens}

    def test_inclui_escalabilidade_opcional_na_consolidacao(self):
        with tempfile.TemporaryDirectory() as pasta:
            self.escrever_relatorios(pasta, self.escalabilidade())
            resultado = verificar_pasta(pasta)
            self.assertTrue(resultado['medicoes_validas'])
            self.assertTrue(resultado['consolidado_consistente'])
            arquivo = Path(pasta) / 'parte2_report.json'
            dados = json.loads(arquivo.read_text())
            dados['experimentos'].pop()
            arquivo.write_text(json.dumps(dados))
            self.assertFalse(verificar_pasta(pasta)['consolidado_consistente'])

    def test_rejeita_escalabilidade_com_tamanhos_incompletos(self):
        with tempfile.TemporaryDirectory() as pasta:
            escalabilidade = self.escalabilidade()
            escalabilidade['experimentos'].pop()
            self.escrever_relatorios(pasta, escalabilidade)
            resultado = verificar_pasta(pasta)
            self.assertFalse(resultado['medicoes_validas'])
            self.assertFalse(resultado['arquivos']['escalabilidade_report.json']['valido'])

    def test_saida_nao_sobrescreve_escalabilidade(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / 'escalabilidade_report.json'
            arquivo.write_text('original')
            with patch('sys.argv', ['verificar', '--pasta', pasta, '--out', str(arquivo)]):
                with self.assertRaises(SystemExit) as erro:
                    main()
            self.assertEqual(erro.exception.code, 2)
            self.assertEqual(arquivo.read_text(), 'original')
