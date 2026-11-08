# Roadmap do projeto

Base: enunciado de 15 páginas, critérios de 31 páginas, mapas fornecidos e declaração oficial de IA. Os documentos em `docs/referencias/` são a referência para requisitos; as etapas abaixo organizam o desenvolvimento, sem resolver os mapas ou produzir análises autorais.

## Situação inicial

- [x] Criar estrutura de pastas e módulos com responsabilidades.
- [x] Preparar locais para testes, dados, saídas e documentos.
- [ ] Implementar as funcionalidades e os testes descritos abaixo.

Etapa 1 concluída: leitor e validação implementados, com 25 testes aprovados, incluindo os oito mapas fornecidos. Algoritmos, modelagem e saídas de avaliação das etapas seguintes ainda não estão prontos.

## Decisões a confirmar desde o início

- [ ] Identificar turma, integrantes (4 ou 5), donos e revisores dos pacotes em `docs/CONTRIBUICOES.md`.
- [ ] Confirmar o status da aprovação do dataset. O checkpoint indicado é 12/10/2026, anterior à criação deste roteiro; não presumir aprovação nem escolher dataset já reservado por outro grupo.
- [ ] Confirmar divergências com as professoras: enunciado pede 6 figuras AVD (4 exploratórias + 2 explanatórias); critérios pedem 4 (2 + 2). Planejar 6 para cobrir ambos até esclarecimento.
- [ ] Confirmar pesos AVD: exploração/storytelling são 3,0/2,0 no enunciado e 2,5/2,5 nos critérios.
- [ ] Definir como reportar passos de BFS: a aresta virtual G -> ALVO não é movimento na grade. Documentar a convenção e esclarecer o gabarito, sem misturar os dois números.
- [ ] Registrar decisões de modelagem e dúvidas sobre casos não explicitados, sem alterar as regras fornecidas.

## Etapa 1 — Leitura e validação

Arquivos: `src/graphs/io.py`, `tests/test_io.py`.

- [x] Ler o mapa de texto e representar sua grade.
- [x] Ignorar comentários iniciados com `;`; documentar o tratamento de linhas vazias sem remover caracteres das casas silenciosamente.
- [x] Validar grade retangular, símbolos, exatamente um S e ao menos um G.
- [x] Identificar início, saídas, chaves e posições dos bônus.
- [x] Numerar bônus a partir de 0 em ordem de linha e coluna.
- [x] Mensagens claras para arquivo ilegível e mapas inválidos.

Concluída quando: testes verificam leitura válida e todos os quatro erros mínimos do enunciado. A leitura não procura caminhos.

## Etapa 2 — Estrutura do grafo e contratos

Arquivo: `src/graphs/graph.py`.

- [ ] Definir lista de adjacência dirigida, nós e pesos.
- [ ] Preservar nós sem saída e ordem de vizinhos.
- [ ] Definir interface comum para os quatro algoritmos, independente do labirinto.
- [ ] Definir formato dos resultados: distâncias, predecessores, caminhos, classificações e ciclos, conforme o algoritmo.
- [ ] Prever transposto para busca de estados-armadilha.

Concluída quando: o grupo consegue representar e conferir à mão um grafo dirigido pequeno; os algoritmos das duas partes podem receber a mesma estrutura.

## Etapa 3 — Primeiro algoritmo: BFS em grafo pequeno

Arquivos: `src/graphs/algorithms.py`, `tests/test_bfs.py`.

- [ ] Implementar BFS próprio em um grafo pequeno criado pelo grupo.
- [ ] Conferir níveis, predecessores, alcançabilidade e reconstrução do caminho.
- [ ] Tratar destino inalcançável.

Concluída quando: o teste de níveis passa e o grupo explica o resultado sem depender do labirinto. Esta etapa antecipa o BFS para ajudar na exploração dos estados.

## Etapa 4 — Modelagem do labirinto

Arquivos: `src/graphs/estados.py`, `tests/test_estados.py`.

- [ ] Desenhar à mão o grafo de estados do m02, como recomendado no enunciado.
- [ ] Definir estado com posição, chaves e bônus consumidos; bitmask é uma escolha, não exigência.
- [ ] Construir G_pos com geometria e esteiras; prever variantes de portas para comparação.
- [ ] Construir G_est explorando apenas estados alcançáveis a partir de S.
- [ ] Gerar movimentos em N, L, S, O; custo sempre da casa de destino.
- [ ] Respeitar portas, chaves permanentes e esteiras (restrição de saída).
- [ ] Bônus +: -4 na primeira entrada, depois 1; fonte *: -2 em toda entrada.
- [ ] Em G, encerrar movimentos do jogo; adicionar ligação de peso 0 para ALVO.
- [ ] Exportar rótulos como `(3,5)|ab|{0,2}`; sem chaves `-`, sem bônus `{}`.
- [ ] Criar mapa mínimo de até 5x7 e calcular estados/arcos à mão para o teste e PDF.
- [ ] Testar esteira contra parede e coleta de chave mudando de camada.

Concluída quando: construção e testes conferem com os exemplos manuais. Não gerar todas as combinações de estados antecipadamente.

## Etapa 5 — DFS, Dijkstra e Bellman-Ford

Arquivos: `src/graphs/algorithms.py` e respectivos testes.

- [ ] DFS próprio com classificação árvore, retorno, avanço e cruzamento; identificar ciclos.
- [ ] Dijkstra próprio com pesos não negativos e recusa clara de qualquer arco negativo.
- [ ] Bellman-Ford próprio com pesos negativos sem ciclo negativo.
- [ ] Detectar e retornar ciclo negativo alcançável, com sequência verificável e custo.
- [ ] Conferir cada algoritmo com grafos pequenos de resposta conhecida.
- [ ] Usar bibliotecas prontas apenas como oráculo dentro de `tests/`, se necessário.

Concluída quando: testes mínimos dos quatro algoritmos passam, inclusive recusa e ciclo negativo. Não duplicar os algoritmos para a Parte 2.

## Etapa 6 — CLI e execução básica da Parte 1

Arquivos: `src/cli.py`, `src/solve.py`.

- [ ] Conectar mapa -> IO -> modelagem -> algoritmo -> resultado.
- [ ] Receber opções dos exemplos de execução do enunciado.
- [ ] Representar status OK, RECUSA, CICLO_NEGATIVO e SEM_SOLUCAO.
- [ ] Executar primeiro m01/m02, depois demais mapas, incluindo m08.
- [ ] Registrar passos, custos e caminhos; distinguir custo de número de movimentos.

Concluída quando: comandos documentados executam de verdade e tratam os casos de erro.

## Etapa 7 — Métricas, comparações e casos especiais

Coordenação: `src/solve.py`; usar módulos auxiliares se necessário para manter responsabilidades claras.

- [ ] Por mapa: ordem, tamanho e densidade dirigida de G_pos e G_est; excluir ALVO das métricas da Seção 3.
- [ ] Teto = casas livres × 2^(número de chaves) × 2^(número de bônus); ocupação = estados / teto.
- [ ] Camadas por conjunto de chaves: métricas dos subgrafos induzidos.
- [ ] Contar arcos entre camadas e identificar casas que os geram.
- [ ] Graus de entrada/saída; maiores graus com desempate pela ordem de leitura do rótulo.
- [ ] Multiplicidade por casa; máximo no m08, quantidade de casas que o atingem e explicação autoral.
- [ ] Becos: estados sem saída fora de G.
- [ ] Comparar portas como chão, como parede e G_est com BFS em m02/m03/m04.
- [ ] Comparar m05 em G_pos (+ sempre -4) e G_est; prova autoral de ausência de ciclo negativo em G_est.
- [ ] Busca no transposto a partir de ALVO para armadilhas de m04 e m07.
- [ ] m01: discussão autoral sobre caminhos de BFS e Dijkstra.
- [ ] m06: exibir ciclo negativo, implementar --fonte-consumivel e mostrar resposta finita.
- [ ] m07: demonstrar ausência de solução e informar estados alcançáveis.

Concluída quando: números, arquivos e explicações são consistentes e verificáveis pelo grupo.

## Etapa 8 — Dois mapas do grupo

Pasta: `data/mapas_grupo/`.

- [ ] Mapa 1: ao menos 3 chaves, esteiras e bônus; menor custo coleta bônus e passa por esteira.
- [ ] Mapa 2: ao menos 20% dos estados alcançáveis são armadilhas.
- [ ] Rodar os mesmos algoritmos e exportações dos mapas fornecidos.
- [ ] Documentar gabarito: estados, arcos, passos BFS e custo com algoritmo adequado.

Concluída quando: ambos cumprem os requisitos e são autorais.

## Etapa 9 — Figuras e interatividade da Parte 1

Arquivo: `src/viz.py`, usando resultados dos módulos anteriores.

- [ ] Percurso de menor custo no m03 e m08, cor mudando a cada chave coletada.
- [ ] Grafo m02 em camadas por chaves, destacando arcos entre camadas.
- [ ] Árvore BFS do m02 com níveis visíveis.
- [ ] Heatmap de multiplicidade do m08.
- [ ] Título, legenda e rótulos em todas as figuras.
- [ ] HTML interativo ou Streamlit com seleção de mapa e algoritmo.
- [ ] Animação com posição, chaves, bônus e custo acumulado.
- [ ] Realce de armadilhas e alternância de camadas.
- [ ] Controle de velocidade ou avanço manual que permita acompanhar o percurso.

Concluída quando: a experiência pode ser acompanhada e todos os itens obrigatórios funcionam. Melhorias para bônus vêm depois do mínimo.

## Etapa 10 — Parte 2: dataset e análise dos dados

Esta frente pode começar em paralelo às etapas da Parte 1, após aprovação do dataset.

- [ ] Dataset dirigido e ponderado com pelo menos 20 mil arestas; não aéreo nem labirinto/grade gerada.
- [ ] Acima de aproximadamente 500 mil arestas: justificar e documentar estratégia de amostragem.
- [ ] Justificar direção quando derivada de fonte não dirigida.
- [ ] Pesos negativos originados dos dados com significado no domínio, sem sortear valores.
- [ ] Formular pergunta de pesquisa e significado de caminho mínimo e ciclo negativo.
- [ ] Exploração de grafos: nós, arcos, graus de entrada/saída e pesos.
- [ ] Exploração AVD: estrutural, distribucional, relacional e outliers.
- [ ] Discutir mecanismo de ausência e justificar tratamento dos faltantes; avaliar outliers.
- [ ] Explorar relações multivariadas quando aplicável ou exploração univariada completa.

Concluída quando: fonte, tratamento, pergunta e modelagem estão documentados e reproduzíveis.

## Etapa 11 — Parte 2: experimentos e visualizações

- [ ] BFS e DFS a partir de pelo menos 3 fontes; relatar ordem, camadas e ciclos conforme aplicável.
- [ ] Dijkstra com pesos não negativos em pelo menos 5 pares; explicar transformação de pesos.
- [ ] Bellman-Ford: caso com peso negativo sem ciclo negativo e caso com ciclo detectado e exibido.
- [ ] Documentar recorte/transformação dos dados quando necessário para os casos exigidos.
- [ ] Medir média de pelo menos 5 execuções por algoritmo e tarefa; memória é opcional.
- [ ] Executar os quatro algoritmos em pelo menos 3 tamanhos (10%, 50%, 100% são exemplos).
- [ ] Comparar crescimento do tempo com complexidade teórica.
- [ ] Gerar gráficos de comparação de tempo, comportamento e caminhos.
- [ ] Planejar 4 visualizações exploratórias + 2 explanatórias; ao menos uma responde à pergunta.
- [ ] Grupo escolhe e justifica gráficos e destaques e escreve notas analíticas autorais.
- [ ] Registrar como a explanatória deriva da exploratória; título, legenda, eixos e legibilidade.
- [ ] Discussão crítica autoral: adequação dos algoritmos, limites dos pesos e resposta à pergunta.

Concluída quando: experimentos são reproduzíveis, resultados têm interpretação do grupo e figuras seguem as regras de AVD.

## Checklist de saídas da Parte 1

- [ ] `out/parte1/arestas_<mapa>.csv` para todos os mapas, incluindo m08 e mapas próprios: origem,destino,movimento,casa_destino,peso.
- [ ] `out/parte1/metricas_global.json` para todos os mapas.
- [ ] `out/parte1/camadas.json` com métricas por camada e arcos entre camadas.
- [ ] `out/parte1/graus_<mapa>.csv`: estado,grau_entrada,grau_saida.
- [ ] `out/parte1/comparacao_modelagem.csv`: mapa,abordagem,passos,caminho_valido,observacao.
- [ ] `out/parte1/solucoes.csv`: mapa,algoritmo,passos,custo,status,caminho.
- [ ] `out/parte1/percurso_m03.json` de menor custo, estado a estado.
- [ ] `out/parte1/ciclo_negativo_m06.json`.
- [ ] `out/parte1/armadilhas_m04.csv` e `armadilhas_m07.csv`.
- [ ] `out/parte1/dfs_classificacao.csv`: mapa,arvore,retorno,avanco,cruzamento.
- [ ] `out/parte1/percurso_m03.png` e `percurso_m08.png`.
- [ ] Demais figuras: camadas m02, árvore BFS m02 e heatmap m08 (nomes livres).
- [ ] `out/parte1/labirinto_interativo.html` ou app Streamlit com instruções.

## Checklist de saídas da Parte 2

- [ ] Proposta de checkpoint aprovada.
- [ ] Dataset ou script de download em `data/dataset_parte2/`.
- [ ] `out/parte2/parte2_report.json`: casos, médias de tempo e escalabilidade.
- [ ] Visualizações comparativas e AVD em `out/parte2/`.
- [ ] Nota analítica autoral de cada visualização e interpretação no PDF.

## Etapa 12 — Documentação, entrega e defesa

- [ ] README com instalação, execução, testes, exemplos e estrutura reais.
- [ ] PDF com manual + técnica: modelagem, resultados, prova m05, correção m06, figuras, análise, limitações e conclusões.
- [ ] Matriz de contribuição efetiva no PDF; commits de todos em pelo menos 2 pacotes.
- [ ] Declaração de IA assinada por todos em `docs/DECLARACAO_IA.pdf` e no Classroom, mesmo se não houver uso.
- [ ] Registrar usos ou links completos; marcação # [IA] onde aplicável; reflexão de 10 a 15 linhas.
- [ ] Conferir execução a partir de uma instalação limpa e testes obrigatórios.
- [ ] Ensaiar mapa surpresa e apresentação de 15 a 20 minutos; todos dominam todo o projeto.
- [ ] Publicar projeto completo no GitHub; entregar o link no Classroom por todos os integrantes. Conferir envio separado da declaração conforme os documentos.

## Datas indicadas nos documentos

- Checkpoint: 12/10/2026.
- Acompanhamentos Grafos: 10, 17, 19 e 24/11/2026.
- Acompanhamentos AVD: 17, 19 e 24/11/2026.
- Entrega por todos: 26/11/2026.
- Apresentações: 26/11 turma A, 01/12 turma B, 03/12 remanescentes e quem cursa só AVD.

Próximo passo de desenvolvimento: Etapa 2, estrutura do grafo e contratos. Etapa 1 verificada em 08/11/2026: 25 testes aprovados.
