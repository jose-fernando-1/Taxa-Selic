import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import requests

# Download dos dados mais recentes
url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=csv"
response = requests.get(url)
with open('selic_efetiva.csv', 'wb') as f:
    f.write(response.content)
