""" Kayo Carvalho Fernandes
"""

import logging
import warnings

import requests_cache
import yfinance as yf
from machine import Preparacao
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error

warnings.filterwarnings("ignore")
logging.disable()
session = requests_cache.CachedSession('yfinance.cache')
session.headers['User-agent'] = 'my-program/1.0'

# > This class is used to get data from the Alpha Vantage API.


if __name__ == '__main__':
    console = Console()
    acao = 'EURUSD=X'
    preparacao = Preparacao()
    ticker = yf.Ticker(acao,session=session)
    dataframe = yf.download(acao,start='2022-09-01',end='2022-11-12',interval='1d',session=session,timeout=2)
    serie = preparacao.preparando_serie(dataframe)
    if serie.shape[0] < 30:
        nome_teste = 'Shapiro Wilk'
        w, p = preparacao.teste_shapiro(serie)
    else:
        nome_teste = "D'Agostino-Pearson"
        w, p = preparacao.teste_person(serie)
    teste = (
        f'[bold]Estatística do teste: [blue]{w}[/blue]\n[bold]p-valor: [blue]{p}')
    if p < 0.05:
        tipo_distribuicao = ("[red]Distruibuição não normal\n")
    else:
        tipo_distribuicao = ("[green]Distribuição normal\n")
    print(Panel(f"\nValores do teste de [bold magenta]{nome_teste}[/bold magenta]\n\n{teste}",
          title="[bold]Teste de confiança[/bold]", subtitle=f"{tipo_distribuicao}"))
    algoritimo2 = preparacao.previsao_prophet(dataframe)
    algoritimo2_dataframe = preparacao.join_daframe_prev(dataframe, algoritimo2)
    resultado_mean2 = mean_absolute_error(
        algoritimo2_dataframe['Close'][:dataframe.shape[0]], algoritimo2_dataframe['fechamento_previsto'][:dataframe.shape[0]])
    resultado_meansq2 = mean_absolute_percentage_error(
        algoritimo2_dataframe['Close'][:dataframe.shape[0]], algoritimo2_dataframe['fechamento_previsto'][:dataframe.shape[0]])
    print('\n')
    print(Panel(f"Teste do Erro absoluto médio [bold magenta]MAE[/bold magenta]\n\nMAE: [blue]{resultado_mean2}[/blue]\nMAPE: [blue]{resultado_meansq2}[/blue]",
          title="[bold]Prophet - Teste de precisão[/bold]", subtitle=f"{'[green]APROVADO[/green]' if resultado_mean2 < 3 else '[red]REPROVADO[/red]'}"))
    table = Table('Data','Fechamento previsto','Mínima previsto','Máxima previsto',title=f"Previsão dos preços da {acao}")
    for i,x in algoritimo2_dataframe.tail(9).iterrows():
        table.add_row(str(x.data),str(x.fechamento_previsto),str(x.minima_previsto),str(x.maxima_previsto))
    console = Console()
    console.print(table)
    console.print(ticker.recommendations)
    console.print()