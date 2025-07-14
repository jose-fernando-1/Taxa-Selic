import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import requests

# Download dos dados mais recentes (últimas 20 entradas)
url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados/ultimos/20?formato=csv"
response = requests.get(url)
with open('selic_recente.csv', 'wb') as f:
    f.write(response.content)

# Ler os dados históricos e os dados recentes
df_historico = pd.read_csv('selic_efetiva.csv')
df_recente = pd.read_csv('selic_recente.csv', sep=';', decimal=',')

# Converter as datas
df_historico['data'] = pd.to_datetime(df_historico['data'])
df_recente['data'] = pd.to_datetime(df_recente['data'], format='%d/%m/%Y')

# Remover as últimas 20 entradas do histórico para evitar duplicação
df_historico = df_historico[:-20]

# Concatenar os dataframes
df = pd.concat([df_historico, df_recente], ignore_index=True)

# Calcular a taxa anual equivalente
dias_uteis_ano = 252
df['taxa_anual'] = ((1 + df['valor']/100) ** dias_uteis_ano - 1) * 100

# Dividir os dados em dois períodos
data_corte = datetime(2000, 1, 1)
df_antigo = df[df['data'] < data_corte]
df_recente = df[df['data'] >= data_corte]

# Criar o gráfico com quatro subplots
fig = make_subplots(
    rows=2, 
    cols=2,
    subplot_titles=(
        'Taxa Diária (1986-1999)',
        'Taxa Diária (2000-presente)',
        'Taxa Anual (1986-1999)',
        'Taxa Anual (2000-presente)'
    ),
    vertical_spacing=0.15,
    horizontal_spacing=0.1
)

# Adicionar os dados para cada período
# Período antigo - Taxa Diária
fig.add_trace(
    go.Scatter(
        x=df_antigo['data'],
        y=df_antigo['valor'],
        name='Taxa Diária (1986-1999)',
        line=dict(color='#2E86C1', width=2)
    ),
    row=1, 
    col=1
)

# Período recente - Taxa Diária
fig.add_trace(
    go.Scatter(
        x=df_recente['data'],
        y=df_recente['valor'],
        name='Taxa Diária (2000-presente)',
        line=dict(color='#2E86C1', width=2)
    ),
    row=1, 
    col=2
)

# Período antigo - Taxa Anual
fig.add_trace(
    go.Scatter(
        x=df_antigo['data'],
        y=df_antigo['taxa_anual'],
        name='Taxa Anual (1986-1999)',
        line=dict(color='#E74C3C', width=2)
    ),
    row=2, 
    col=1
)

# Período recente - Taxa Anual
fig.add_trace(
    go.Scatter(
        x=df_recente['data'],
        y=df_recente['taxa_anual'],
        name='Taxa Anual (2000-presente)',
        line=dict(color='#E74C3C', width=2)
    ),
    row=2, 
    col=2
)

# Configurar o layout
fig.update_layout(
    height=900,
    title_text='Evolução da Taxa SELIC',
    showlegend=True,
    template='plotly_white',
    hovermode='x unified',
)

# Configurar os eixos Y para escala logarítmica
for i in range(1, 3):
    for j in range(1, 3):
        fig.update_yaxes(
            type='log',
            row=i, 
            col=j,
            ticksuffix='%',
            title_text='Taxa SELIC (%)'
        )

# Configurar os eixos X
fig.update_xaxes(title_text='Data', row=2, col=1)
fig.update_xaxes(title_text='Data', row=2, col=2)

# Salvar o gráfico como HTML
fig.write_html('grafico_selic_periodos.html')

print("✅ Gráfico por períodos gerado com sucesso em 'grafico_selic_periodos.html'")