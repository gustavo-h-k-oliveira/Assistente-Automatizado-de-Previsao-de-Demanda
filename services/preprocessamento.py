# services/preprocessamento.py
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from models import DemandaPreprocessada
from database import engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import delete

SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def preprocessar_dados(df: pd.DataFrame):
    # Renomear colunas para padrão esperado
    colunas_renomear = {
        "Data": "data",
        "Produto": "produto",
        "Categoria": "categoria",
        "Região": "regiao",
        "Quantidade": "quantidade",
        "Preço Unitário": "preco_unitario"
    }
    df = df.rename(columns=colunas_renomear)

    # Limpeza e tratamento de strings
    df["produto"] = df["produto"].astype(str).str.strip().str.lower()
    df["categoria"] = df["categoria"].astype(str).str.strip().str.lower()
    df["regiao"] = df["regiao"].astype(str).str.strip().str.lower()

    # Garantir tipo de data
    df["data"] = pd.to_datetime(df["data"], errors='coerce')
    df["quantidade"] = pd.to_numeric(df["quantidade"], errors="coerce")
    df["preco_unitario"] = pd.to_numeric(df["preco_unitario"], errors="coerce")

    # Remover linhas inválidas
    df = df.dropna(subset=["data", "produto", "categoria", "quantidade", "preco_unitario", "regiao"])

    # Ordenar para cálculos temporais
    df = df.sort_values("data")

    # Features derivadas
    df["ano"] = df["data"].dt.year
    df["mes"] = df["data"].dt.month
    df["dia_semana"] = df["data"].dt.day_name()
    df["dia_mes"] = df["data"].dt.day
    df["semana_ano"] = df["data"].dt.isocalendar().week
    df["fim_de_semana"] = df["data"].dt.weekday >= 5
    df["dias_desde_inicio"] = (df["data"] - df["data"].min()).dt.days
    df["tendencia_local"] = df["quantidade"].diff().fillna(0)

    # Limpa a tabela existente
    async with SessionLocal() as session:
        await session.execute(delete(DemandaPreprocessada))
        await session.commit()

        for _, row in df.iterrows():
            registro = DemandaPreprocessada(
                produto=row["produto"],
                categoria=row["categoria"],
                data=row["data"],
                quantidade=float(row["quantidade"]),
                regiao=row["regiao"],
                preco_unitario=float(row["preco_unitario"]),
                ano=int(row["ano"]),
                mes=int(row["mes"]),
                dia_semana=row["dia_semana"],
                dia_mes=int(row["dia_mes"]),
                semana_ano=int(row["semana_ano"]),
                fim_de_semana=bool(row["fim_de_semana"]),
                dias_desde_inicio=int(row["dias_desde_inicio"]),
                tendencia_local=float(row["tendencia_local"])
            )
            session.add(registro)

        await session.commit()
