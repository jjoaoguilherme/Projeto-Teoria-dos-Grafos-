DECLARAÇÃO DE IA: https://docs.google.com/document/d/1sCr8p8y-t-Wttt3G8kXXsjhVLVZ4CMPh/edit?usp=sharing&ouid=112702963052965676955&rtpof=true&sd=true


## Métricas globais da Parte 1

Para gerar ordem, tamanho, densidade, teto teórico e ocupação de todos os mapas:

```powershell
python -m src.cli --metricas --out out/parte1
```

Para um único mapa, acrescentar `--mapa data/mapas/m02_uma_chave.txt`. O comando grava `out/parte1/metricas_global.json`, sem executar caminhos mínimos e sem apagar as métricas dos outros mapas. Convenções e modo fonte consumível em [docs/METRICAS.md](docs/METRICAS.md).
