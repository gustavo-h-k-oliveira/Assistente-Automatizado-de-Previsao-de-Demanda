# modelos/treinar_modelo_lightgbm.py
import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from models import DemandaPreprocessada
import asyncio

DATABASE_URL = "sqlite+aiosqlite:///./data/demanda.db"

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def carregar_dados():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(DemandaPreprocessada))
        dados = result.scalars().all()
        df = pd.DataFrame([{
            "produto": d.produto,
            "categoria": d.categoria,
            "data": d.data,
            "quantidade": d.quantidade,
            "regiao": d.regiao,
            "ano": d.ano,
            "mes": d.mes,
            "dia_semana": d.dia_semana,
            "preco_unitario": d.preco_unitario,
            "dia_mes": d.dia_mes,
            "semana_ano": d.semana_ano,
            "fim_de_semana": d.fim_de_semana,
            "dias_desde_inicio": d.dias_desde_inicio,
            "tendencia_local": d.tendencia_local
        } for d in dados])
        return df

def preparar_e_treinar(df):
    df["data"] = pd.to_datetime(df["data"])

    # Codificação das variáveis categóricas
    df_encoded = pd.get_dummies(df, columns=["produto", "categoria", "regiao", "dia_semana"])

    # Features e variável alvo
    X = df_encoded.drop(columns=["quantidade", "data"])
    y = df_encoded["quantidade"]

    # Divisão em treino e teste
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Treinamento do modelo LightGBM
    modelo = lgb.LGBMRegressor(random_state=42)
    modelo.fit(X_train, y_train)

    # Avaliação do modelo
    y_pred = modelo.predict(X_test)
    print("\n🌟 Avaliação do modelo LightGBM:")
    print("MSE:", mean_squared_error(y_test, y_pred))
    print("R²:", r2_score(y_test, y_pred))

    # Salvar o modelo treinado
    joblib.dump(modelo, "modelos/modelo_lightgbm.pkl")
    print("✅ Modelo salvo em 'modelos/modelo_lightgbm.pkl'.")

async def main():
    df = await carregar_dados()
    if df.empty:
        print("⚠️ Nenhum dado disponível para modelagem.")
        return
    preparar_e_treinar(df)

if __name__ == "__main__":
    asyncio.run(main())
