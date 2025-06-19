# services/previsao.py
import joblib
import pandas as pd

from models import PrevisaoHistorico
from sqlalchemy.ext.asyncio import AsyncSession
from database import SessionLocal

def carregar_modelo(modelo_nome="random_forest"): # Modelo padrão
    caminho = f"modelos/modelo_{modelo_nome}.pkl"
    return joblib.load(caminho), modelo_nome

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

async def salvar_previsao(dados, resultado, modelo_nome):
    async with SessionLocal() as session:
        nova = PrevisaoHistorico(
            produto=dados.produto,
            categoria=dados.categoria,
            regiao=dados.regiao,
            preco_unitario=dados.preco_unitario,
            quantidade_prevista=resultado,
            modelo_usado=modelo_nome
        )
        session.add(nova)
        await session.commit()
