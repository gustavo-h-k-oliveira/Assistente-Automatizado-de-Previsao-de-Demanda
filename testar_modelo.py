import pandas as pd
import joblib

# Carregar o modelo treinado
modelo = joblib.load("modelos/modelo_demanda.pkl")

# Criar uma entrada de teste (mock)
# Você pode editar os valores conforme suas categorias
entrada = {
    "ano": 2024,
    "mes": 6,
    "preco_unitario": 25.50,
    
    # Suponha que essas sejam as categorias existentes no treinamento
    "produto_Produto A": 1,
    "produto_Produto B": 0,
    "categoria_Categoria 1": 1,
    "categoria_Categoria 2": 0,
    "regiao_Sul": 1,
    "regiao_Norte": 0,
    "dia_semana_Monday": 1,
    "dia_semana_Tuesday": 0,
    "dia_semana_Wednesday": 0,
    "dia_semana_Thursday": 0,
    "dia_semana_Friday": 0,
    "dia_semana_Saturday": 0,
    "dia_semana_Sunday": 0
}

# Garantir que todas as colunas estejam presentes (modelo espera as mesmas features)
colunas_treinadas = modelo.feature_names_in_
df_teste = pd.DataFrame([entrada])

# Adicionar colunas ausentes com valor 0
for col in colunas_treinadas:
    if col not in df_teste.columns:
        df_teste[col] = 0

# Reordenar as colunas
df_teste = df_teste[colunas_treinadas]

# Predição
predicao = modelo.predict(df_teste)

print(f"\n🔮 Previsão de demanda estimada: {int(round(predicao[0]))} unidades")
