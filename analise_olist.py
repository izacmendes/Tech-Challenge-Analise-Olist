# =============================================================================
# TECH CHALLENGE - ANÁLISE ESTRATÉGICA DA OLIST
# Autora: Izabella Costa Mendes
# =============================================================================

import os
import pandas as pd

# =============================================================================
# 0. CONFIGURAÇÃO DE CAMINHOS
# =============================================================================

DIRETORIO_SCRIPT = os.path.dirname(os.path.abspath(__file__))
PASTA_DADOS = os.path.join(DIRETORIO_SCRIPT, '..', 'data')

# =============================================================================
# 1. CONFIGURAÇÕES INICIAIS
# =============================================================================

pd.set_option('display.float_format', '{:,.2f}'.format)

print("=" * 60)
print("INICIANDO ANÁLISE DA OLIST")
print("=" * 60)

# =============================================================================
# 2. CARREGAMENTO DOS DADOS
# =============================================================================

print("Carregando datasets...")

orders = pd.read_csv(
    os.path.join(PASTA_DADOS, 'olist_orders_dataset.csv')
)

items = pd.read_csv(
    os.path.join(PASTA_DADOS, 'olist_order_items_dataset.csv')
)

reviews = pd.read_csv(
    os.path.join(PASTA_DADOS, 'olist_order_reviews_dataset.csv')
)

products = pd.read_csv(
    os.path.join(PASTA_DADOS, 'olist_products_dataset.csv')
)

translation = pd.read_csv(
    os.path.join(PASTA_DADOS, 'product_category_name_translation.csv')
)

print("Datasets carregados com sucesso.")

# =============================================================================
# 3. TRATAMENTO DAS DATAS
# =============================================================================

print("Tratando colunas de data...")

orders['order_purchase_timestamp'] = pd.to_datetime(
    orders['order_purchase_timestamp']
)

orders['order_delivered_customer_date'] = pd.to_datetime(
    orders['order_delivered_customer_date']
)

orders['order_estimated_delivery_date'] = pd.to_datetime(
    orders['order_estimated_delivery_date']
)

# =============================================================================
# 4. CRESCIMENTO DOS PEDIDOS
# =============================================================================

print("Calculando evolução dos pedidos...")

orders['mes'] = orders['order_purchase_timestamp'].dt.to_period('M')

pedidos_mes = (
    orders
    .groupby('mes')
    .size()
    .reset_index(name='quantidade_pedidos')
)

pedidos_mes = pedidos_mes[
    pedidos_mes['quantidade_pedidos'] >= 100
].copy()

pedidos_mes['data_mes'] = pedidos_mes['mes'].dt.to_timestamp()

print("Pedidos por mês calculados.")

# =============================================================================
# 5. EVOLUÇÃO DA RECEITA
# =============================================================================

print("Calculando receita mensal...")

receita = orders.merge(
    items,
    on='order_id',
    how='inner'
)

receita['mes'] = (
    receita['order_purchase_timestamp']
    .dt.to_period('M')
)

receita_mes = (
    receita
    .groupby('mes')['price']
    .sum()
    .reset_index()
)

receita_mes['price'] = receita_mes['price'].round(2)

receita_mes['data_mes'] = (
    receita_mes['mes']
    .dt.to_timestamp()
)

print("Receita mensal calculada.")

# =============================================================================
# 6. SATISFAÇÃO DOS CLIENTES
# =============================================================================

print("Calculando satisfação dos clientes...")

avaliacoes = (
    reviews['review_score']
    .value_counts()
    .sort_index()
    .reset_index()
)

avaliacoes.columns = [
    'review_score',
    'quantidade'
]

nota_media = reviews['review_score'].mean()

print(f"Nota média: {nota_media:.2f}")

# =============================================================================
# 7. EFICIÊNCIA LOGÍSTICA
# =============================================================================

print("Calculando atrasos logísticos...")

orders_delivered = (
    orders[
        orders['order_status'] == 'delivered'
    ]
    .copy()
)

orders_delivered['dias_atraso'] = (
    orders_delivered['order_delivered_customer_date']
    -
    orders_delivered['order_estimated_delivery_date']
).dt.days

atrasados = (
    orders_delivered['dias_atraso'] > 0
).sum()

total_entregues = len(orders_delivered)

percentual_atraso = (
    atrasados / total_entregues
)

print(
    f"Percentual de atraso: {percentual_atraso:.2f}%"
)

# =============================================================================
# 8. IMPACTO DOS ATRASOS NA SATISFAÇÃO
# =============================================================================

print("Analisando impacto dos atrasos...")

analise = orders_delivered.merge(
    reviews,
    on='order_id',
    how='inner'
)

analise['atrasou'] = (
    analise['dias_atraso'] > 0
)

logistica_satisfacao = (
    analise
    .groupby('atrasou')['review_score']
    .mean()
    .reset_index()
)

logistica_satisfacao['review_score'] = (
    logistica_satisfacao['review_score']
    .round(2)
)

# =============================================================================
# 9. TOP 10 CATEGORIAS POR RECEITA
# =============================================================================

print("Calculando categorias mais lucrativas...")

produtos_categoria = items.merge(
    products[
        [
            'product_id',
            'product_category_name'
        ]
    ],
    on='product_id',
    how='left'
)

produtos_categoria = produtos_categoria.merge(
    translation,
    on='product_category_name',
    how='left'
)

top_categorias = (
    produtos_categoria
    .groupby(
        'product_category_name_english'
    )['price']
    .sum()
    .sort_values(
        ascending=False
    )
    .head(10)
    .reset_index()
)

top_categorias['price'] = (
    top_categorias['price']
    .round(2)
)

# =============================================================================
# 10. KPIs PARA POWER BI
# =============================================================================

print("Calculando KPIs...")

kpis_dashboard = pd.DataFrame({
    'Pedidos Totais': [
        orders['order_id'].nunique()
    ],
    'Receita Total': [
        round(items['price'].sum(), 2)
    ],
    'Nota Média': [
        round(nota_media, 2)
    ],
    'Percentual de Atraso': [
        round(percentual_atraso, 2)
    ]
})

print(kpis_dashboard)

# =============================================================================
# 11. EXPORTAÇÃO DOS CSVs
# =============================================================================

print("Exportando arquivos para Power BI...")

pedidos_mes[
    ['data_mes', 'quantidade_pedidos']
].to_csv(
    os.path.join(
        PASTA_DADOS,
        'pedidos_mes.csv'
    ),
    index=False,
    sep=';'
)

receita_mes[
    ['data_mes', 'price']
].to_csv(
    os.path.join(
        PASTA_DADOS,
        'receita_mes.csv'
    ),
    index=False,
    sep=';',
    decimal=','
)

avaliacoes.to_csv(
    os.path.join(
        PASTA_DADOS,
        'avaliacoes.csv'
    ),
    index=False,
    sep=';'
)

logistica_satisfacao.to_csv(
    os.path.join(
        PASTA_DADOS,
        'logistica_satisfacao.csv'
    ),
    index=False,
    sep=';',
    decimal=','
)

top_categorias.to_csv(
    os.path.join(
        PASTA_DADOS,
        'top_categorias.csv'
    ),
    index=False,
    sep=';',
    decimal=','
)

kpis_dashboard.to_csv(
    os.path.join(
        PASTA_DADOS,
        'kpis_dashboard.csv'
    ),
    index=False,
    sep=';',
    decimal=','
)

# =============================================================================
# 12. RESUMO FINAL
# =============================================================================

print("\nPROCESSAMENTO CONCLUÍDO COM SUCESSO!\n")

print("Arquivos gerados:")

print("- pedidos_mes.csv")
print("- receita_mes.csv")
print("- avaliacoes.csv")
print("- logistica_satisfacao.csv")
print("- top_categorias.csv")
print("- kpis_dashboard.csv")