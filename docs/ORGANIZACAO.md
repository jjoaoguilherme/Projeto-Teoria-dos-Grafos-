# Organizacao do repositorio

- O antigo main.py foi transferido integralmente, sem editar seu conteudo, para src/graphs/io.py, pois sua funcao principal e leitura e validacao.
- Esse arquivo ainda e um script: executa ao ser importado, inclui exibicao e direcoes, exige exatamente uma saida e usa o caminho fixo mapas/m02_uma_chave.txt. Nada disso foi corrigido nesta reorganizacao.
- Para executar a versao existente, abrir o terminal na raiz deste repositorio e usar: python src/graphs/io.py
- mapas/ foi preservada para manter o caminho usado no codigo. data/mapas/ contem copias identicas da versao do grupo, inclusive suas quebras de linha. A unificacao depende de alterar esse caminho futuramente.
- O README.md do grupo foi preservado integralmente, incluindo o link de declaracao de IA.
- A documentacao de estrutura anteriormente preparada esta em docs/ESTRUTURA_E_EXECUCAO.md, com seu conteudo original.
- A implementacao de IO anterior gerada por IA e seus testes estao em docs/referencias/versao_ia/, preservados como referencia, sem substituir o trabalho do grupo.
- tests/test_io.py e um ponto de partida; os 25 testes citados na documentacao anterior validam a versao de IA, nao o script atual do grupo.
- ROADMAP.md e a documentacao anterior foram copiados sem revisao de conteudo; suas afirmacoes sobre a etapa 1 precisam ser reavaliadas contra o codigo do grupo antes de marcar a etapa como concluida.
- Nenhum commit nem push foi realizado nesta reorganizacao.
