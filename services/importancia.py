# services/importancia.py
import matplotlib.pyplot as plt
from xgboost import plot_importance
import joblib

def gerar_grafico_importancia(caminho_modelo="modelos/modelo_xgboost.pkl", caminho_imagem="static/importancia.png"):
    modelo = joblib.load(caminho_modelo)
    fig, ax = plt.subplots(figsize=(10, 6))
    plot_importance(modelo, ax=ax)
    plt.tight_layout()
    fig.savefig(caminho_imagem)
    plt.close(fig)
