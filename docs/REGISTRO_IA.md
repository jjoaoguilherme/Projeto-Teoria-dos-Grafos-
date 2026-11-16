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
