# Taxa SELIC - Visualização Histórica

[![Atualizar Dados SELIC](../../actions/workflows/update-data.yml/badge.svg)](../../actions/workflows/update-data.yml)

Visualização interativa da evolução histórica da Taxa SELIC, utilizando dados do Banco Central do Brasil.

## Sobre

Este projeto apresenta uma visualização gráfica da Taxa SELIC desde 1986, dividida em períodos para melhor compreensão da evolução das taxas ao longo do tempo.

## Dados

Os dados são obtidos diretamente da API do Banco Central do Brasil e atualizados automaticamente todos os dias úteis às 15:00 (horário de Brasília).

## Visualização

Acesse a visualização em: [https://seu-usuario.github.io/nome-do-repositorio](https://seu-usuario.github.io/nome-do-repositorio)

## Atualizações Automáticas

O projeto usa GitHub Actions para:
- Atualizar os dados automaticamente em dias úteis às 15:00 (horário de Brasília)
- Gerar novos gráficos quando houver mudanças nos dados
- Publicar as atualizações automaticamente no GitHub Pages

Você também pode forçar uma atualização manual indo na aba "Actions", selecionando o workflow "Atualizar Dados SELIC" e clicando em "Run workflow".

## Desenvolvimento

Para executar localmente:

1. Clone o repositório
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Execute o script de atualização:
   ```bash
   python atualizar_diariamente.py
   ```

## Status da Última Atualização

- 🤖 Atualização automática: Todos os dias úteis às 15:00 (Brasília)
- 📊 Fonte dos dados: API do Banco Central do Brasil
- 📈 Visualização: GitHub Pages