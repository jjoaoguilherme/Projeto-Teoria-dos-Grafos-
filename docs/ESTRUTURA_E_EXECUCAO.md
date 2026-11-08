# Projeto Final de Teoria dos Grafos e AVD

Projeto 2026.2: labirintos com chaves e portas (Parte 1) e comparação de algoritmos em um dataset maior (Parte 2).

## Estado atual

Etapa 1 concluída: leitura e validação de mapas em `src/graphs/io.py`, com 25 testes aprovados em `tests/test_io.py`, incluindo os oito mapas fornecidos. Modelagem, algoritmos, CLI e visualizações ainda não estão implementados; os demais arquivos de teste são pontos de partida.

Comece por [ROADMAP.md](ROADMAP.md). Os documentos originais estão em `docs/referencias/`.

## Ambiente

Python 3.11 ou superior. No terminal PowerShell do VS Code, na raiz do projeto:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Não é necessário ativar o ambiente virtual para usar os comandos acima. No VS Code, selecione `.venv\Scripts\python.exe` como interpretador Python.

## Organização

- `src/cli.py`: entrada por linha de comando.
- `src/solve.py`: coordenação das tarefas das duas partes.
- `src/graphs/io.py`: leitura e validação dos mapas e do dataset.
- `src/graphs/graph.py`: grafo dirigido em lista de adjacência.
- `src/graphs/estados.py`: grafos de posições e de estados dos labirintos.
- `src/graphs/algorithms.py`: BFS, DFS, Dijkstra e Bellman-Ford próprios.
- `src/viz.py`: figuras e interface interativa.
- `tests/`: testes mínimos exigidos.
- `data/mapas/`: os oito mapas originais.
- `data/mapas_grupo/`: dois mapas autorais, a criar.
- `data/dataset_parte2/`: dataset aprovado ou script de download.
- `out/parte1/` e `out/parte2/`: saídas geradas pelo programa.
- `docs/`: documentação, contribuição e declaração de IA.

## Comandos previstos

Estes comandos são o contrato de execução a implementar, não funcionalidades já disponíveis:

```powershell
python -m src.cli --mapa data/mapas/m03_tres_chaves.txt --alg BFS --out out/parte1/
python -m src.cli --mapa data/mapas/m05_bonus.txt --alg BELLMAN_FORD --out out/parte1/
python -m src.cli --mapa data/mapas/m06_fonte.txt --alg BELLMAN_FORD --fonte-consumivel --out out/parte1/
python -m src.cli --mapa data/mapas/m04_esteiras.txt --armadilhas --out out/parte1/
python -m src.cli --mapa data/mapas/m03_tres_chaves.txt --interactive --out out/parte1/
python -m src.cli --dataset data/dataset_parte2/ --benchmark --out out/parte2/
```

Para testar a etapa 1: `python -m pytest tests/test_io.py -q`. A aprovação destes testes verifica a entrada dos mapas, não a corretude dos algoritmos futuros.

## Leitura de um mapa

Depois de preparar o ambiente, execute na raiz:

```powershell
python -c "from src.graphs.io import ler_mapa; mapa = ler_mapa('data/mapas/m02_uma_chave.txt'); print(mapa.grade); print('Inicio:', mapa.inicio); print('Chaves:', mapa.chaves)"
```

`ler_mapa` aceita caminho em texto ou `Path` e retorna um objeto `Mapa` com `grade`, `inicio`, `saidas`, `chaves`, `bonus`, `altura` e `largura`. As coordenadas começam em zero. Chaves são associadas a todas as suas posições; bônus recebem IDs por linha e coluna. Fontes e portas permanecem na grade.

O leitor aceita UTF-8 com ou sem BOM e quebras de linha Windows ou Unix. Ignora comentários com `;` na primeira coluna e linhas vazias no final. Linhas vazias dentro da grade são rejeitadas; espaços são preservados e rejeitados como símbolos inválidos. Mensagens indicam linhas do arquivo e colunas a partir de um. Arquivos ilegíveis e mapas inválidos geram `ErroMapa`, uma subclasse de `ValueError`. A existência de solução será verificada nas próximas etapas.

## Regras essenciais

Sem bibliotecas de algoritmos prontos. `networkx` pode ser usado apenas em `tests/` como oráculo. O grupo deve observar as diretrizes de IA dos documentos originais, registrar os usos e entregar `docs/DECLARACAO_IA.pdf` assinado por todos. Esse PDF ainda não foi produzido.
