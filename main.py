from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import os
from typing import Optional
from database import engine, Base
from sqlalchemy import select
from contextlib import asynccontextmanager

from services.preprocessamento import preprocessar_dados  # <-- use o novo preprocessamento
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

    # Chama o novo preprocessamento e salva no banco
    await preprocessar_dados(df)

    return {
        "message": "Arquivo carregado e pré-processado com sucesso.",
        "rows": len(df),
        "columns": df.columns.tolist()
    }

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
        return [
            {
                "produto": r.produto,
                "categoria": r.categoria,
                "data": str(r.data),
                "quantidade": r.quantidade,
                "regiao": r.regiao,
                "preco_unitario": r.preco_unitario,
                "ano": r.ano,
                "mes": r.mes,
                "dia_semana": r.dia_semana,
            }
            for r in registros
        ]

@app.get("/preprocessados/")
async def listar_preprocessados(limit: int = 20):
    async with SessionLocal() as session:
        result = await session.execute(select(DemandaPreprocessada).limit(limit))
        registros = result.scalars().all()
        return [r.__dict__ for r in registros]
