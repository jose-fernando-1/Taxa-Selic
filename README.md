# Taxa SELIC e Indicadores do Banco Central

[![Atualizar Dados SELIC](../../actions/workflows/update-data.yml/badge.svg)](../../actions/workflows/update-data.yml)

Painel com integração oficial às APIs SGS e PTAX do Banco Central do Brasil para consultar indicadores econômicos históricos e atuais.

## Sobre

O projeto foi refatorado para trabalhar com múltiplas séries econômicas em uma arquitetura extensível. A camada Python agora centraliza coleta, normalização, armazenamento deduplicado, endpoints internos e geração de gráficos.

## Dados

Os dados são obtidos diretamente de APIs oficiais do Banco Central do Brasil:

- SGS para séries temporais econômicas.
- PTAX OData para câmbio oficial.

Séries já configuradas:

- Selic diária
- Meta Selic
- CDI
- IPCA
- IGP-M
- Dólar PTAX
- Euro PTAX

## Visualização

O frontend agora consome endpoints internos expostos pela API FastAPI.

## Atualizações Automáticas

O projeto usa GitHub Actions para:
- Atualizar os dados automaticamente em dias úteis às 15:00 (horário de Brasília)
- Atualizar os armazenamentos locais sem duplicidade
- Publicar as atualizações automaticamente no GitHub Pages

Você também pode forçar uma atualização manual indo na aba "Actions", selecionando o workflow "Atualizar Dados SELIC" e clicando em "Run workflow".

## Desenvolvimento

Para executar localmente:

1. Clone o repositório
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Execute a atualização local:
   ```bash
   python atualizar_diariamente.py
   ```
4. Suba a API interna:
   ```bash
   uvicorn app:app --reload
   ```
5. Abra o frontend em um servidor local apontando para a mesma origem da API.

## Endpoints internos

- `GET /api/health`
- `GET /api/series`
- `GET /api/series/{slug}?start=2024-01-01&end=2026-12-31`
- `GET /api/series/{slug}/latest`
- `GET /api/charts/{slug}`
- `POST /api/refresh`
- `POST /api/refresh/{slug}`

## Estrutura

- `taxa_selic/series.py`: catálogo de séries e metadados
- `taxa_selic/bcb.py`: clientes oficiais SGS/PTAX com timeout e tratamento de erro
- `taxa_selic/storage.py`: armazenamento CSV deduplicado
- `taxa_selic/service.py`: regras de atualização, filtro e export legada
- `taxa_selic/api.py`: endpoints internos para o frontend

## Status da Última Atualização

- 🤖 Atualização automática: Todos os dias úteis às 15:00 (Brasília)
- 📊 Fonte dos dados: API do Banco Central do Brasil
- 📈 Visualização: GitHub Pages