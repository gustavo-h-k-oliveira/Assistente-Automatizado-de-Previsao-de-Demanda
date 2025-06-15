# schemas.py
from pydantic import BaseModel
from datetime import date

class DadosPrevisao(BaseModel):
    produto: str
    categoria: str
    data: date
    regiao: str
    preco_unitario: float
    quantidade_anterior: float  # usado para calcular tendência local
