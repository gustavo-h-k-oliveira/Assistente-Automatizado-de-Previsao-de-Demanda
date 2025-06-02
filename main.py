from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import os

app = FastAPI(title="Predição de Demanda - API")

# Armazenamento temporário em memória
data_store = {"df": None}

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Arquivo deve ser .xlsx ou .xls")
    
    # Salva arquivo temporariamente
    file_location = f"./data/{file.filename}"
    os.makedirs("./data", exist_ok=True)
    with open(file_location, "wb") as f:
        f.write(await file.read())

    # Lê o arquivo com pandas
    try:
        df = pd.read_excel(file_location)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao ler arquivo: {e}")

    # Armazena em memória
    data_store["df"] = df

    return {"message": "Arquivo carregado com sucesso", "columns": df.columns.tolist()}

@app.get("/dados/")
async def get_data():
    df = data_store.get("df")
    if df is None:
        raise HTTPException(status_code=404, detail="Nenhum dado carregado")
    
    # Retorna os primeiros 10 registros
    return JSONResponse(content=df.head(10).to_dict(orient="records"))

@app.get("/")
async def root():
    return {"message": "API de Predição de Demanda - Online"}
wfx