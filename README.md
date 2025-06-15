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
