from sqlalchemy import Column, Integer, String, Float, Date
from database import Base

class DemandaPreprocessada(Base):
    __tablename__ = "demanda_preprocessada"

    id = Column(Integer, primary_key=True, index=True)
    produto = Column(String, index=True)
    categoria = Column(String)
    data = Column(Date)
    quantidade = Column(Float)
    preco_unitario = Column(Float)
    regiao = Column(String)
    ano = Column(Integer)
    mes = Column(Integer)
    dia_semana = Column(String)
