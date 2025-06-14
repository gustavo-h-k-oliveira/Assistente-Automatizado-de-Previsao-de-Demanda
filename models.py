from sqlalchemy import Column, Integer, String, Float
from database import Base

class RegistroDemanda(Base):
    __tablename__ = "demanda"

    id = Column(Integer, primary_key=True, index=True)
    produto = Column(String, index=True)
    data = Column(String)         # Ajustaremos para datetime mais tarde
    quantidade = Column(Float)
