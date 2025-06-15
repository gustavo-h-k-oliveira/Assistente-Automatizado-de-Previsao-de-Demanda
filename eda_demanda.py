import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from models import DemandaPreprocessada
import asyncio

DATABASE_URL = "sqlite+aiosqlite:///./data/demanda.db"  # Altere para o nome do seu arquivo .db

# Configuração do engine e sessão
engine = create_async_engine(DATABASE_URL, echo=False)
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
            "preco_unitario": d.preco_unitario
        } for d in dados])
        return df

def analisar_dados(df):
    print("\n🔍 Primeiras linhas:")
    print(df.head())
    
    print("\n📊 Resumo estatístico:")
    print(df.describe())

    # Converter data se necessário
    df["data"] = pd.to_datetime(df["data"])

    # Gráfico 1: Demanda ao longo do tempo
    plt.figure(figsize=(12, 4))
    df.groupby("data")["quantidade"].sum().plot(title="Demanda ao longo do tempo")
    plt.ylabel("Quantidade vendida")
    plt.tight_layout()
    plt.savefig("data/graphs/demanda_ao_longo_do_tempo.png")
    plt.close()

    # Gráfico 2: Top 5 produtos mais vendidos
    top_produtos = df.groupby("produto")["quantidade"].sum().sort_values(ascending=False).head(5)
    plt.figure(figsize=(8, 4))
    top_produtos.plot(kind="bar", title="Top 5 Produtos Mais Vendidos", color="orange")
    plt.ylabel("Quantidade")
    plt.tight_layout()
    plt.savefig("data/graphs/top_5_produtos.png")
    plt.close()

    # Gráfico 3: Distribuição por dia da semana
    ordem_dias = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    plt.figure(figsize=(8, 4))
    sns.barplot(data=df, x="dia_semana", y="quantidade", order=ordem_dias)
    plt.title("Demanda por Dia da Semana")
    plt.tight_layout()
    plt.savefig("data/graphs/demanda_por_dia_da_semana.png")
    plt.close()

async def main():
    df = await carregar_dados()
    if df.empty:
        print("⚠️ Nenhum dado encontrado.")
        return
    analisar_dados(df)

if __name__ == "__main__":
    asyncio.run(main())
