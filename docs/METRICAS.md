# Métricas globais dos labirintos

As funções de cálculo e exportação estão em `src/graphs/metricas.py`. A opção da CLI não executa algoritmos de caminhos mínimos: constrói os grafos e conta seus nós e arcos. Assim, funciona também para mapas sem solução ou com ciclos negativos.

## Executar

Na raiz do projeto, para os oito mapas fornecidos e os mapas próprios em `data/mapas_grupo/`:

```powershell
python -m src.cli --metricas --out out/parte1
```

Para um único mapa:

```powershell
python -m src.cli --metricas --mapa data/mapas/m02_uma_chave.txt --out out/parte1
```

A saída é `out/parte1/metricas_global.json`. Cada mapa tem uma entrada com o nome do arquivo sem extensão. Executar um único mapa atualiza somente sua entrada, preservando as demais. Nomes dos mapas devem ser distintos. A opção `--metricas` não pode ser combinada com `--alg`.

## Campos e convenções

- `G_pos.ordem`: número de casas não parede, inclusive portas e casas inalcançáveis. Usa o modelo com portas como chão.
- `G_pos.tamanho`: quantidade de arcos dirigidos do grafo de posições.
- `G_pos.densidade`: tamanho / (ordem * (ordem - 1)).
- `G_est.ordem`: quantidade de estados alcançáveis, excluindo o nó virtual ALVO.
- `G_est.tamanho`: quantidade de arcos cujas duas pontas são estados reais; não conta ligações para ALVO.
- `G_est.densidade`: a mesma fórmula, usando ordem e tamanho sem ALVO. Para ordem menor que 2, densidade é 0.
- `casas_livres`: todas as casas diferentes de #, inclusive portas e saídas.
- `chaves` e `numero_chaves`: tipos distintos entre a, b, c, d. Duas casas com a mesma chave não criam um novo tipo de inventário.
- `numero_bonus`: quantidade de casas +; cada uma tem consumo independente.
- `teto_teorico`: casas_livres * 2 ** numero_chaves * 2 ** numero_bonus no modo normal.
- `taxa_ocupacao`: G_est.ordem / teto_teorico, representada como fração entre 0 e 1; multiplicar por 100 para porcentagem.

Não há teto de inventário ou ocupação separados para G_pos, pois ele não representa inventário. Esses dois valores comparam G_est com as combinações teóricas possíveis.

## Fonte consumível

```powershell
python -m src.cli --metricas --mapa data/mapas/m06_fonte.txt --fonte-consumivel --out out/parte1
```

A variante recebe a chave `m06_fonte_fonte_consumivel`, sem substituir a execução normal. `numero_fontes_consumiveis` informa as fontes que passam a ter histórico de consumo. Nesse modo, o teto inclui um fator 2 para cada fonte, além das chaves e bônus. As métricas de G_pos não mudam, pois esse modelo não guarda consumo.

## Testes

```powershell
python -m unittest discover -s tests -p test_metricas.py -v
python -m unittest discover -s tests -v
```

Os testes de métricas conferem contas manuais de grafos pequenos, limites da densidade, exclusão de ALVO, inventário, casas inalcançáveis, exportação incremental e execução da CLI. Camadas, graus por estado, rankings e multiplicidade estão descritos abaixo. A análise completa de armadilhas continua pendente.


## Origem única dos indicadores

- `calcular_metricas_labirinto` calcula as métricas usando o grafo de estados já construído. A quantidade de casas livres vem da ordem de G_pos, sem uma segunda contagem da grade.
- `calcular_metricas_mapa` é a entrada de conveniência para o comando `--metricas`: lê o arquivo, constrói os estados e delega ao mesmo cálculo.
- `calcular_metricas_percurso` fornece passos, custo final, custo médio por movimento e casas distintas. O custo acumulado do caminho é calculado na resolução e apenas consultado aqui.
- A resolução normal inclui `metricas_globais` e `metricas_percurso` em `resultado_*.json`. Na exportação, o mesmo objeto de métricas globais atualiza `metricas_global.json`.
- Os campos antigos `passos`, `custo` e `estados_alcancaveis` são mantidos por compatibilidade e copiam os indicadores centrais; não têm fórmulas próprias.

O HTML mostra os valores exportados: não calcula média, quantidade de estados, densidade, teto ou ocupação. Somente o progresso da animação é calculado na apresentação, pois depende do passo atual. O conjunto de casas visitadas usado para desenhar o rastro é visual; não recalcula o indicador de casas distintas do percurso completo.

É possível importar `metricas_global.json` diretamente no HTML, inclusive sem um percurso carregado. Resultados antigos continuam permitindo animação e exibição dos campos existentes; médias e casas distintas ficam indisponíveis até regenerar o relatório. A conversão de densidade e ocupação para texto ou porcentagem é somente formatação.


## Graus, rankings, becos, multiplicidade e camadas

O comando `--metricas` agora gera o bloco completo para todos os mapas:

- `metricas_global.json`: resumo global anterior, rankings de entrada/saída, becos e multiplicidade.
- `graus_<mapa>.csv`: uma linha por estado real, com estado, grau_entrada e grau_saida. Exclui ALVO e todos os arcos incidentes nele; G tem saída zero.
- `camadas.json`: subgrafos induzidos por conjunto de chaves e resumo dos arcos entre camadas. Estados com diferentes bônus consumidos podem estar na mesma camada.

`calcular_detalhes_estados` percorre uma vez os arcos reais para contar graus e ligações internas/entre camadas. O ranking informa o estado vencedor e seu grau; empates são resolvidos em ordem lexicográfica do rótulo completo, sem converter as coordenadas para números. A saída é determinística e não depende da ordem de exploração.

Becos são estados com saída zero fora de G. Não são a análise completa de estados-armadilha, que continua pendente. A multiplicidade contém cada casa não parede, com zero para casas sem estados alcançáveis, além do máximo, quantidade de casas que o atingem e suas posições. Isso fornece os dados para o heatmap de m08; a figura e sua interpretação no relatório continuam pendentes.

Em `camadas.json`, a camada sem chaves se chama `-`. Cada camada informa ordem, tamanho e densidade, considerando apenas arcos com as duas pontas na camada. `arcos_entre_camadas` informa o total, contagens por par de camadas e as posições e chaves das casas de destino responsáveis pela transição. ALVO não pertence a nenhuma camada. A fórmula de densidade é compartilhada com as métricas globais.

`calcular_pacote_metricas` reúne os cálculos reutilizando os estados existentes; `calcular_pacote_mapa` lê e constrói os estados quando a entrada é um arquivo. A resolução comum reutiliza esse pacote nas exportações. CSVs e camadas são gravados separadamente para não duplicar os graus dentro dos relatórios globais. A variante de fonte consumível mantém o sufixo `_fonte_consumivel` nos três arquivos, sem apagar a execução normal.

A geração pode ser repetida para um mapa sem apagar os dados dos demais. Os resultados detalhados ficam nos arquivos exportados; os indicadores já existentes do HTML continuam lendo o mesmo resumo global.
