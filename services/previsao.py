# services/previsao.py
import joblib
import pandas as pd
from datetime import datetime

def carregar_modelo():
    return joblib.load("modelos/modelo_xgboost.pkl")

def preparar_entrada(dados):
    data = pd.to_datetime(dados.data)

    entrada = pd.DataFrame([{
        "produto": dados.produto,
        "categoria": dados.categoria,
        "data": data,
        "quantidade": dados.quantidade_anterior,
        "regiao": dados.regiao,
        "preco_unitario": dados.preco_unitario,
        "ano": data.year,
        "mes": data.month,
        "dia_semana": data.day_name(),
        "dia_mes": data.day,
        "semana_ano": data.isocalendar().week,
        "fim_de_semana": data.weekday() >= 5,
        "dias_desde_inicio": (data - pd.to_datetime("2022-01-01")).days,
        "tendencia_local": 0  # ou use lógica para estimar
    }])

    # Conversão de categorias para dummies (igual ao treino)
    entrada = pd.get_dummies(entrada)
    return entrada
