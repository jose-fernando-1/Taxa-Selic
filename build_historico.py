
import pandas as pd
from datetime import datetime, timedelta

codigo_serie = 11
data_inicio = datetime(1986, 6, 4)
data_fim = datetime.today()
max_anos = 10

def formatar_data(d):
    return d.strftime('%d/%m/%Y')

dfs = []
data_atual = data_inicio

while data_atual < data_fim:
    data_proxima = min(data_atual.replace(year=data_atual.year + max_anos), data_fim)
    url = (
        f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo_serie}/dados"
        f"?formato=csv&dataInicial={formatar_data(data_atual)}&dataFinal={formatar_data(data_proxima)}"
    )
    print(f"Baixando de {formatar_data(data_atual)} até {formatar_data(data_proxima)}")
    df = pd.read_csv(url, sep=';', decimal=',')
    dfs.append(df)
    data_atual = data_proxima + timedelta(days=1)

df_total = pd.concat(dfs, ignore_index=True)
df_total['data'] = pd.to_datetime(df_total['data'], dayfirst=True)
df_total['valor'] = pd.to_numeric(df_total['valor'])
df_total = df_total.sort_values('data')
df_total.to_csv('selic_efetiva.csv', index=False)

print("✅ Base histórica salva em 'selic_efetiva.csv'")