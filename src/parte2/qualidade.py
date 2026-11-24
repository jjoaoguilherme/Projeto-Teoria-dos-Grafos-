"""Conferências dos atributos do TSV, sem excluir ou substituir valores."""
from datetime import datetime
from hashlib import sha256
import json
from math import isfinite


def iniciar_qualidade(colunas):
    return {
        'faltantes_por_coluna': dict.fromkeys(colunas, 0),
        'espacos_externos_por_coluna': dict.fromkeys(colunas, 0),
        'duplicatas_exatas': 0,
        'datas_invalidas': 0,
        'linhas_datas_invalidas_exemplo': [],
        'properties': {'dimensoes_encontradas': {}, 'vetores_invalidos': 0,
                       'linhas_invalidas_exemplo': []},
    }


def conferir_atributos(registro, qualidade, assinaturas, linha):
    for coluna in qualidade['faltantes_por_coluna']:
        valor = registro.get(coluna)
        if valor is None or not valor.strip():
            qualidade['faltantes_por_coluna'][coluna] += 1
        elif valor != valor.strip():
            qualidade['espacos_externos_por_coluna'][coluna] += 1

    assinatura = sha256(json.dumps(registro, ensure_ascii=False,
                                   separators=(',', ':')).encode('utf-8')).digest()
    if assinatura in assinaturas:
        qualidade['duplicatas_exatas'] += 1
    assinaturas.add(assinatura)

    data = (registro.get('TIMESTAMP') or '').strip()
    if data:
        try:
            datetime.fromisoformat(data)
        except ValueError:
            qualidade['datas_invalidas'] += 1
            exemplos = qualidade['linhas_datas_invalidas_exemplo']
            if len(exemplos) < 5:
                exemplos.append(linha)

    vetor = registro.get('PROPERTIES')
    if vetor and vetor.strip():
        partes = vetor.split(',')
        propriedades = qualidade['properties']
        dimensoes = propriedades['dimensoes_encontradas']
        dimensao = str(len(partes))
        dimensoes[dimensao] = dimensoes.get(dimensao, 0) + 1
        try:
            valido = len(partes) == 86 and all(isfinite(float(p)) for p in partes)
        except ValueError:
            valido = False
        if not valido:
            propriedades['vetores_invalidos'] += 1
            if len(propriedades['linhas_invalidas_exemplo']) < 5:
                propriedades['linhas_invalidas_exemplo'].append(linha)
