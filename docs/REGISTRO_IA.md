# Registro de apoio de IA

Este arquivo é um apoio organizacional e não substitui o formulário oficial nem as assinaturas.

## Uso em 08/11/2026

- Ferramenta: Codex. Modelo/plano: preencher conforme a conta e a sessão.
- Pedido: preparar a estrutura de arquivos e um roadmap baseado no enunciado.
- Material produzido: esqueleto de pastas, documentação de planejamento e módulos/testes com descrições de responsabilidades, sem implementação funcional.
- Arquivos fornecidos copiados sem alteração para referência; mapas extraídos do ZIP original.
- Integrante responsável por conferir: a preencher.
- Verificação humana e alterações: a preencher.

## Conversas anteriores

Registrar também os usos anteriores desta conversa, inclusive o exemplo completo de leitura e validação fornecido no chat. Esse exemplo não foi colocado nos arquivos Python desta estrutura. Conferir a classificação de cada uso com as diretrizes oficiais, sem presumir que apenas registrar torna um uso permitido.

## Implementação da etapa 1 em 08/11/2026

- Pedido do usuário: implementar a etapa 1.
- Ferramenta: Codex.
- Produzido: implementação de `src/graphs/io.py`, testes em `tests/test_io.py` e atualização de README e roadmap.
- Verificação automatizada: 25 testes aprovados, incluindo leitura dos oito mapas originais.
- Código apoiado por IA marcado com `# [IA]` nos dois arquivos Python.
- Conferência e compreensão por integrante do grupo: pendente.
- Atenção à classificação: o documento oficial inclui geração de `io.py` nos usos proibidos; o registro não altera essa classificação nem autoriza sua entrega acadêmica.

## Conclusão do Bellman-Ford em 11/11/2026

- Ferramenta: Codex.
- Pedido: completar o algoritmo mantendo a lógica inicial de lista de arestas e relaxamento.
- Produzido: função reutilizável em `src/graphs/algorithms.py`, predecessores, reconstrução de caminhos, detecção e reconstrução de ciclo negativo e identificação dos destinos afetados.
- Preservado o grafo de exemplo do usuário para execução direta; corrigida a posição do laço de repetições.
- Verificação: sete testes aprovados em `tests/test_bellman_ford.py`; exemplo retorna A=0, B=1, C=3 e D=6.
- Código apoiado por IA identificado com `# [IA]`. Estudo e conferência pelo integrante: pendentes.
- Integração com os mapas depende da construção do grafo de estados, ainda não implementada.

## Integração do Bellman-Ford em 14/11/2026

- Pedido: adaptar o algoritmo para funcionar com os mapas do projeto.
- Ferramenta: Codex. Mantida a orientação atualizada informada pelo usuário na conversa, sem novo documento da professora.
- Produzido: exploração de estados alcançáveis, rótulos, pesos consumíveis, ALVO, integração em `solve.py` e CLI para BELLMAN_FORD, exportações e documentação em `docs/BELLMAN_FORD.md`.
- Ajustadas as funções existentes para esteiras, saídas terminais e estados imutáveis; leitor aceita comentários, BOM e múltiplas saídas, preservando seu retorno legado (a última saída no terceiro item; a integração identifica todas na grade).
- Verificação: 13 testes unitários/de integração aprovados; execução dos oito mapas fornecidos, incluindo m08. m06 detecta ciclo negativo e m07 informa ausência de solução.

## Antes da entrega

- Preencher o modelo oficial ou registrar links completos conforme permitido.
- Marcar os trechos de código feitos com apoio de IA com `# [IA] ferramenta – finalidade`.
- Escrever a reflexão autoral de 10 a 15 linhas.
- Obter assinatura de todos e exportar para `docs/DECLARACAO_IA.pdf`.


## Testes da estrutura de grafo e do grafo de posições em 16/11/2026

- Ferramenta utilizada: Codex.
- Finalidade: criação de testes automatizados para conferir os contratos dos grafos.
- `tests/test_graph.py`: 10 testes escritos com apoio de IA, cobrindo direção e ordem dos arcos, nós sem saída, laços, arcos paralelos, graus, transposto, proteção das consultas, pesos inválidos e compatibilidade com Bellman-Ford e mapas.
- `tests/test_grafo_posicoes.py`: 12 testes escritos com apoio de IA, cobrindo os modos de portas como chão/parede, casas inalcançáveis, custos de destino, bônus fixos, ordem N/L/S/O, esteiras, saídas terminais e preservação da matriz. Inclui os oito mapas fornecidos nos dois modos.
- Verificação automatizada: `python -m unittest discover -s tests -v`; 35 testes aprovados na suíte completa, incluindo os 22 testes acima e os 13 testes anteriores de Bellman-Ford e integração.
- Revisão e conferência pelo grupo: pendentes; não se presume que a execução automatizada substitua a verificação humana.
- Esta entrada registra somente a autoria dos testes; o preenchimento referente aos demais arquivos fica sob responsabilidade do usuário.


## Testes de métricas globais em 19/11/2026

- Ferramenta: Codex.
- Arquivo: `tests/test_metricas.py`, com 17 testes escritos com apoio de IA.
- Finalidade: conferir ordem, tamanho e densidade em exemplos calculados à mão; exclusão de ALVO e seus arcos; teto e ocupação com chaves, bônus e fonte consumível; casas inalcançáveis; preservação dos grafos; exportação incremental e opções da CLI.
- Verificação automatizada: `python -m unittest discover -s tests -q`; 52 testes aprovados no total, incluindo os 17 novos. A captura dos subprocessos usa UTF-8 explicitamente para compatibilidade com Windows.
- Revisão humana pelo grupo: pendente. Esta entrada registra somente os testes; o registro referente ao restante do código fica com o usuário.


## Testes de centralização das métricas em 19/11/2026

- Ferramenta: Codex.
- Arquivo: `tests/test_metricas.py`, com 8 testes adicionais escritos com apoio de IA, totalizando 25 testes nesse arquivo.
- Finalidade: conferir percurso vazio, percurso sem movimentos, posições repetidas e custo negativo; garantir que a resolução não reconstrói os estados; comparar campos legados com os indicadores centrais; verificar consistência entre as exportações e situações de recusa, ciclo negativo e ausência de solução.
- Verificação: suíte completa com 60 testes aprovados. Também foi executada uma verificação temporária no Edge sem janela para importação de JSON, compatibilidade com relatórios antigos, animação e ausência de erros JavaScript; o painel foi inspecionado em tamanhos desktop e celular.
- Esta entrada registra somente os testes e verificações; os registros dos demais arquivos ficam com o usuário. Revisão humana do grupo: pendente.


## Testes das métricas detalhadas em 22/11/2026

- Ferramenta: Codex.
- Arquivo criado: `tests/test_metricas_detalhadas.py`, com 9 testes de apoio à validação de graus, rankings, becos, multiplicidade e camadas.
- Casos: contas manuais em SaG, bônus sem mudança de camada, esteira contra parede, múltiplas saídas, empate lexicográfico, exportação incremental e variante consumível, proteção de camadas.json inválido e invariantes dos dez mapas mais m06 consumível.
- Ajustado o teste de exportação em `tests/test_metricas.py` para exigir também camadas.json e o CSV de graus.
- Verificação: 69 testes aprovados; CSVs dos dez mapas conferidos quanto à quantidade de estados e soma dos graus. O restante do registro de implementação fica com o usuário. Revisão humana do grupo: pendente.


## Testes da conclusão técnica da Parte 1 em 22/11/2026

- Ferramenta: Codex. Registro limitado aos testes, conforme autorizado pelo usuário.
- Arquivos: tests/test_bfs.py, test_dfs.py, test_dijkstra.py, test_io.py, test_estados.py e test_entrega_parte1.py.
- Finalidade: níveis/caminhos BFS; quatro tipos de arco e ciclos DFS; Dijkstra com peso zero e recusa de negativo inalcançável; mapas inválidos, comentários e múltiplas saídas; mapa mínimo SaG contado à mão; armadilhas; comparação de portas; requisitos dos mapas próprios e presença das entregas.
- Verificação: 84 testes aprovados e 67 subtestes. O registro dos demais trechos e a revisão humana ficam com o usuário.


## Testes do leitor de dataset da Parte 2

- Ferramenta: Codex. Registro restrito aos testes, conforme autorizado.
- Arquivo: tests/test_dataset_parte2.py; nove casos executados, incluindo parametrização de registros inválidos.
- Conferências: direção, pesos, preservação de atributos, arcos paralelos e laços, campos ausentes/extras, política estrita e registro de rejeições, cabeçalhos inválidos, arquivo inexistente, dataset vazio, exportação e uso dos algoritmos existentes.
- Suíte: 93 testes aprovados e 67 subtestes. O TSV real não estava disponível; os testes usam apenas entradas pequenas temporárias. Revisão do grupo: pendente.

## Infraestrutura de experimentos da Parte 2 em 23/11/2026

- Ferramenta: Codex.
- Finalidade: implementação da infraestrutura de medição e dos testes pelo Codex, seguindo o passo a passo discutido e os critérios confirmados pelo usuário.
- Arquivos: `src/parte2/experimentos.py` e `tests/test_experimentos.py`.
- Etapas: preparar a entrada fora da medição; medir chamadas com `time.perf_counter`; repetir pelo menos cinco vezes; guardar tempos individuais e média; registrar ambiente e exportar JSON. As validações internas dos algoritmos estão incluídas no tempo da chamada.
- Verificação: 66 testes aprovados na suíte completa, incluindo seis novos testes da infraestrutura; demonstração pela CLI executou os quatro algoritmos cinco vezes cada e exportou JSON válido em pasta temporária.
- Demonstração disponível com `python -m src.parte2.experimentos --demonstracao`; usa grafo pequeno e salva `out/parte2/demonstracao_report.json`. Não constitui os experimentos finais do dataset nem resultados de escalabilidade.
- Pendências: integração com o grafo preparado e casos dos demais integrantes, amostragem, execuções finais, gráficos e interpretação autoral. O relatório final pode ser gravado por `exportar_relatorio` em `out/parte2/parte2_report.json`.

## Amostragem para escalabilidade em 23/11/2026

- Ferramenta: Codex.
- Finalidade: implementação da infraestrutura de amostragem e seus testes para a atividade de desempenho e escalabilidade.
- Arquivos: `src/parte2/amostragem.py`, `tests/test_amostragem.py` e instruções no README.
- Etapas: selecionar proporções de vértices com semente local fixa; construir amostras aninhadas por subgrafos induzidos; preservar direção e pesos; permitir fontes/destinos obrigatórios; registrar método, arredondamento, vértices selecionados e tamanhos reais.
- Verificação: 73 testes aprovados na suíte completa, incluindo sete novos testes de reprodução, preservação dos arcos, cópia independente, gerador aleatório, parâmetros, arredondamento e integração com o medidor.

## Verificação dos experimentos da Parte 2 em 24/11/2026

- Ferramenta: Codex.
- Finalidade: implementação da conferência automatizada das medições e da consistência do relatório consolidado.
- Arquivos: `src/parte2/verificar_experimentos.py`, `tests/test_verificar_experimentos.py` e `out/parte2/verificacao_experimentos.json`.
- Etapas: conferir pelo menos cinco repetições, tempos finitos não negativos, média, unidade, tamanhos e status; comparar o consolidado com os relatórios BFS/DFS, Dijkstra e Bellman-Ford, incluindo a multiplicidade dos registros.
- Verificação: cinco novos testes aprovados; 13 experimentos conferidos e consolidação consistente. A execução da suíte completa encontrou quatro erros de importação pela ausência de pytest no interpretador disponível.

## Gráficos de desempenho em 24/11/2026

- Ferramenta: Codex.
- Finalidade: implementação da geração de figuras a partir das medições JSON existentes.
- Arquivos: `src/parte2/visualizações.py`, `tests/test_graficos_desempenho.py`, README e figuras em `out/parte2/graficos/`.
- Etapas: validar as medições, separar tarefas por quantidades de vértices/arcos e exportar PNG/SVG com médias, tempos individuais e desvio-padrão amostral, mantendo rótulos, unidades e fonte.
- Verificação: três figuras geradas nos dois formatos e inspecionadas visualmente; suíte executada com pytest no ambiente virtual, com 122 testes e 89 subtestes aprovados.

## Executor de escalabilidade em 24/11/2026

- Ferramenta: Codex.
- Finalidade: implementação da conexão entre amostragem e medição dos quatro algoritmos, com escala configurável.
- Arquivos: `src/parte2/escalabilidade.py`, `tests/test_escalabilidade.py` e README.
- Etapas: carregar o CSV preparado; receber origem, proporções, semente e limite opcional; construir amostras; medir quatro algoritmos com pelo menos cinco repetições; registrar hash da entrada e transformação dos pesos de Dijkstra; exportar relatório separado.
- Verificação: cinco novos testes aprovados, incluindo execução pela CLI com CSV temporário, 12 medições, transformação dos pesos e preservação da entrada; suíte completa com 127 testes e 89 subtestes aprovados.

## Geração de gráficos de escalabilidade em 24/11/2026

- Ferramenta: Codex.
- Finalidade: implementação do gerador de gráficos para os relatórios de escalabilidade.
- Arquivos: `src/parte2/graficos_escalabilidade.py`, `tests/test_graficos_escalabilidade.py` e README.
- Etapas: validar três tamanhos por algoritmo e consistência das amostras; ordenar as séries; desenhar quatro painéis com médias, desvio-padrão e tamanhos dos grafos; exportar PNG e SVG.
- Verificação: três novos testes e seis subcasos aprovados; prévia inspecionada com dados simulados em pasta temporária; suíte completa com 130 testes e 95 subtestes aprovados.

## Execução de escalabilidade com recorte em 24/11/2026

- Ferramenta: Codex.
- Finalidade: execução dos experimentos no recorte autorizado, consolidação, figuras e tabela numérica de apoio.
- Arquivos: relatórios e figuras em `out/parte2/`, `src/parte2/consolidar.py`, `src/parte2/tabela_complexidades.py`, verificador, testes e README.
- Etapas: piloto; recorte de 2.000 vértices, semente 42 e origem subredditdrama; amostras de 200, 1.000 e 2.000 vértices; cinco execuções dos quatro algoritmos; registro de hashes, ambiente, arcos e alcance; consolidação de 25 experimentos e exportação de gráficos e tabela.
- Ajuste técnico: deduplicação da fila de propagação dos ciclos negativos em Bellman-Ford; medições refeitas após o ajuste. Conferência paralela por agentes de verificação e complexidades.
- Verificação: 60 execuções de escalabilidade concluídas, relatórios consistentes e gráficos inspecionados; suíte com 135 testes e 95 subtestes aprovados.
