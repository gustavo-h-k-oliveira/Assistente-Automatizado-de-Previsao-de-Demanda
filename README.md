# Assistente Automatizado de Previsão de Demanda

O Assistente Automatizado de Previsão de Demanda é responsável por receber planilhas Excel, garantir o seu upload em um local predefinido, analisar os dados utilizando algoritmos de aprendizado de máquina e fornecer previsões detalhadas de demanda para cada item listado.

## Estrutura inicial do dataset

Para a realização de testes, será utilizado uma base de dados fictícia em `.xlsx` com as seguintes colunas:

| Data       | Produto        | Categoria   | Quantidade | Preço Unitário | Região   |
| ---------- | -------------- | ----------- | ---------- | -------------- | -------- |
| 2024-01-01 | Café Premium   | Bebidas     | 250        | 9.90           | Sul      |
| 2024-01-02 | Leite Integral | Laticínios  | 180        | 4.50           | Sudeste  |
| 2024-01-02 | Pão de Forma   | Panificados | 300        | 6.20           | Nordeste |
| ...        | ...            | ...         | ...        | ...            | ...      |

Os valores foram gerados aleatoriamente em um período de 2 meses.

### Métricas dos modelos

1. **Regressão Linear**

    * ***MSE***: 13936.888401142032

    * ***R²***: 0.013103048003078599 → explica 1,3% da variação (muito baixa)

2. **XGBosst**

    * ***MSE***: 11539.833851819072

    * ***R²***: 0.1828429325746832 → explica 18,2% da variação

## Atualização do dataset

Incluindo novos campos derivados (`dia_mes`, `semana_ano`, `fim_de_semana`, `dias_desde_inicio`, `tendencia_local`) como features nos modelos e atualizando o banco de dados com as novas colunas.

### Novas métricas dos modelos

1. **Regressão Linear**

    * ***MSE***: 7170.282486176355

    * ***R²***: 0.3279559588311879 → explica 32,7% da variação

2. **XGBosst**

    * ***MSE***: 6804.083921733312

    * ***R²***: 0.36227839502432 → explica 36,2% da variação

## Modelo Preditivo

Recebe dados e retorna uma previsão de demanda utilizando o endpoint `/prever` com base no modelo carregado em `previsao.py`.

Exemplo de uso:

```json
{
  "produto": "Produto A",
  "categoria": "Bebidas",
  "data": "2023-08-15",
  "regiao": "Nordeste",
  "preco_unitario": 5.0,
  "quantidade_anterior": 130
}
```

Retorna:

```json
{
  "previsao": 230.82
}
```

## Adição do modelo Random Forest e LightGBM

Métrica de avaliação dos modelos:

1. **Random Forest**

    * ***MSE***: 6084.352241860466

    * ***R²***: 0.4297361817477131 → Explica 42,9% da variação

2. **LightGBM**

    * ***MSE***: 6353.568801762835

    * ***R²***: 0.40450350992269624 → Explica 40,4% da variação

## Otimização dos hiperparâmetros para o modelo LightGBM

Após a busca dos melhores hiperparâmetros usando o `GridSearchCV` do `scikit-learn`, foi definido os seguintes parâmetros:

```js
param_grid = {
    'num_leaves': [10, 20, 30],
    'min_data_in_leaf': [3, 5, 10],
    'max_depth': [3, 5, 7],
    'learning_rate': [0.01, 0.05, 0.1],
}
```

Ao avaliar o modelo com os melhores hiperparâmetros, chegou-se às seguintes métricas:

* ***MSE***: 5985.443458487636

* ***R²***: 0.4390065359650144 → Explica 43,9% da variação
