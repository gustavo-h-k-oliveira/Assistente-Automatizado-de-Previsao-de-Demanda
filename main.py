from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import os
from typing import Optional

# Cria instância do app FastAPI
app = FastAPI(title="API de Predição de Demanda")

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

    # Armazena o DataFrame em memória
    data_store["df"] = df

    return {
        "message": "Arquivo carregado com sucesso.",
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
