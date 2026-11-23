DECLARAÇÃO DE IA: https://docs.google.com/document/d/1sCr8p8y-t-Wttt3G8kXXsjhVLVZ4CMPh/edit?usp=sharing&ouid=112702963052965676955&rtpof=true&sd=true


## Métricas globais da Parte 1

Para gerar ordem, tamanho, densidade, teto teórico e ocupação de todos os mapas:

```powershell
python -m src.cli --metricas --out out/parte1
```

Para um único mapa, acrescentar `--mapa data/mapas/m02_uma_chave.txt`. O comando grava `out/parte1/metricas_global.json`, sem executar caminhos mínimos e sem apagar as métricas dos outros mapas. Convenções e modo fonte consumível em [docs/METRICAS.md](docs/METRICAS.md).

Os resultados de uma resolução também incluem as métricas globais e os indicadores do percurso, calculados em `src/graphs/metricas.py`. O HTML lê esses indicadores e permite importar `metricas_global.json`; não repete as fórmulas.

## Amostragem para escalabilidade da Parte 2

`src/parte2/amostragem.py` prepara subgrafos induzidos por 10%, 50% e 100% dos vértices, com semente configurável (42 por padrão). As amostras são aninhadas, preservam direção, pesos, laços, arcos paralelos e a ordem original de inserção. As quantidades são arredondadas para cima; proporções que resultem no mesmo tamanho são recusadas. Não há alteração do grafo original.

```python
from src.parte2.amostragem import criar_amostras
from src.parte2.experimentos import medir_algoritmo, exportar_relatorio

# grafo_preparado deve ser um Grafo construído a partir da base do grupo.
# origem deve ser uma das fontes definidas para o experimento.
amostras = criar_amostras(grafo_preparado, semente=42, obrigatorios=[origem])
experimentos = []
for item in amostras:
    grafo = item['grafo']
    experimentos.append(medir_algoritmo(
        'BFS', grafo.vertices, grafo.arestas, origem,
        identificacao={'amostragem': item['metadados']}))
exportar_relatorio(experimentos)
```

Os metadados incluem semente, método, proporções solicitadas/reais, tamanhos originais/obtidos e vértices selecionados/obrigatórios. A reprodução exige os mesmos dados, ordem de entrada e runtime. A amostragem ocorre fora da medição do algoritmo. A lista de obrigatórios condiciona a seleção e deve caber na menor amostra.
