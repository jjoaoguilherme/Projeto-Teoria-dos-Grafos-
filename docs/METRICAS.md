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

Os testes de métricas conferem contas manuais de grafos pequenos, limites da densidade, exclusão de ALVO, inventário, casas inalcançáveis, exportação incremental e execução da CLI. Camadas, graus por estado, rankings, multiplicidade e armadilhas serão implementados separadamente.
