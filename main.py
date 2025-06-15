from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import os
from typing import Optional
from database import engine, Base
from sqlalchemy import select
from contextlib import asynccontextmanager
import datetime

from utils import preprocessar_dataframe
from models import DemandaPreprocessada
from database import SessionLocal

# Novo gerenciador de ciclo de vida
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

# Cria instância do app FastAPI com lifespan
app = FastAPI(title="API de Predição de Demanda", lifespan=lifespan)

# Armazena temporariamente o DataFrame carregado
data_store = {"df": None}

@app.get("/")
async def root():
    return {"message": "API de Predição de Demanda ativa. Use /docs para testar os endpoints."}


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """
    Recebe um arquivo .xlsx ou .xls e armazena seus dados em memória.
    """
    # Verifica extensão
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Formato inválido. Envie um arquivo .xlsx ou .xls.")

    # Cria diretório para salvar o arquivo temporariamente
    os.makedirs("data", exist_ok=True)
    file_location = f"data/{file.filename}"

    # Salva arquivo localmente
    try:
        with open(file_location, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar o arquivo: {e}")

    # Tenta ler com pandas
    try:
        df = pd.read_excel(file_location)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao ler o arquivo Excel: {e}")

    if df.empty:
        raise HTTPException(status_code=400, detail="Arquivo não contém dados.")

    # Armazena o DataFrame no data_store
    data_store["df"] = df

    # Novo bloco de código sugerido
    df["Data"] = pd.to_datetime(df["Data"])
    df["ano"] = df["Data"].dt.year
    df["mes"] = df["Data"].dt.month
    df["dia_semana"] = df["Data"].dt.day_name()

    async with SessionLocal() as session:
            for _, row in df.iterrows():
                registro = DemandaPreprocessada(
                    produto=str(row["Produto"]),
                    categoria=str(row["Categoria"]),
                    data=row["Data"].date() if isinstance(row["Data"], (pd.Timestamp, datetime.datetime)) else row["Data"],
                    quantidade=float(row["Quantidade"]),
                    preco_unitario=float(row["Preço Unitário"]),
                    regiao=str(row["Região"]),
                    ano=int(row["ano"]),
                    mes=int(row["mes"]),
                    dia_semana=str(row["dia_semana"])
                )
                session.add(registro)
            await session.commit()

    return {
        "message": "Arquivo carregado com sucesso.",
        "rows": len(df),
        "columns": df.columns.tolist()
    }

@app.get("/preprocessar/")
async def preprocessar():
    async with SessionLocal() as session:
        result = await session.execute(select(DemandaPreprocessada))
        dados = result.scalars().all()

        df = pd.DataFrame([{
            "Data": r.data,
            "Produto": r.produto,
            "Categoria": getattr(r, "categoria", "indefinida"),
            "Quantidade": r.quantidade,
            "Preço Unitário": getattr(r, "preco_unitario", 0.0),
            "Região": getattr(r, "regiao", "indefinida")
        } for r in dados])

        df_processado = preprocessar_dataframe(df)

        # Salvar os dados no banco
        for _, row in df_processado.iterrows():
            registro = DemandaPreprocessada(
                produto=row["Produto"],
                categoria=row["Categoria"],
                data=row["Data"].date() if isinstance(row["Data"], (pd.Timestamp, datetime.datetime)) else row["Data"],
                quantidade=row["Quantidade"],
                preco_unitario=row["Preço Unitário"],
                regiao=row["Região"],
                ano=row["ano"],
                mes=row["mes"],
                dia_semana=row["dia_semana"]
            )
            session.add(registro)

        await session.commit()

        return df_processado.to_dict(orient="records")

@app.get("/dados/")
async def get_data(linhas: Optional[int] = 10):
    """
    Retorna os primeiros registros do DataFrame carregado.
    """
    df = data_store.get("df")

    if df is None:
        raise HTTPException(status_code=404, detail="Nenhum dado foi carregado. Faça upload primeiro.")

    try:
        # Prepara os dados para retorno JSON
        data_json = df.head(linhas).fillna("").astype(str).to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar dados: {e}")

    return JSONResponse(content=data_json)

@app.get("/registros/")
async def listar_registros():
    async with SessionLocal() as session:
        result = await session.execute(
            select(DemandaPreprocessada).limit(10)
        )
        registros = result.scalars().all()
        return [r.__dict__ for r in registros]

@app.get("/preprocessados/")
async def listar_preprocessados(limit: int = 20):
    async with SessionLocal() as session:
        result = await session.execute(select(DemandaPreprocessada).limit(limit))
        registros = result.scalars().all()
        return [r.__dict__ for r in registros]
    