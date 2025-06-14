import pandas as pd

def preprocessar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(how="all")

    df["Data"] = pd.to_datetime(df["Data"], errors='coerce')
    df["Produto"] = df["Produto"].astype(str).str.strip().str.lower()
    df["Categoria"] = df["Categoria"].astype(str).str.strip().str.lower()
    df["Região"] = df["Região"].astype(str).str.strip().str.lower()
    df["Quantidade"] = pd.to_numeric(df["Quantidade"], errors="coerce")
    df["Preço Unitário"] = pd.to_numeric(df["Preço Unitário"], errors="coerce")

    df = df.dropna(subset=["Data", "Produto", "Categoria", "Quantidade", "Preço Unitário", "Região"])

    df["ano"] = df["Data"].dt.year
    df["mes"] = df["Data"].dt.month
    df["dia_semana"] = df["Data"].dt.day_name()

    return df
