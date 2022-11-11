""" Kayo Carvalho Fernandes
"""

import warnings
from datetime import datetime, timedelta

import pandas as pd
# import requests_cache
import yfinance as yf
from machine import Preparacao
from rich import print
from rich.console import Console
from rich.panel import Panel
from sklearn.metrics import mean_absolute_error, mean_squared_error

warnings.filterwarnings("ignore")


# > This class is used to get data from the Alpha Vantage API.


if __name__ == '__main__':
    console = Console()
    acao = 'PETR4.SA'
    preparacao = Preparacao()
    dataframe = yf.download(acao,start='2022-08-01',end='2022-11-09',interval='1d')
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
    print(Panel(f"Valores do teste de [bold magenta]{nome_teste}[/bold magenta]\n\n{teste}",
          title="[bold]Teste de confiança[/bold]", subtitle=f"{tipo_distribuicao}"))
    algoritimo = preparacao.teste_treinamento_auto_arima(serie)
    resultado_mean = mean_absolute_error(
        algoritimo['Fechamento'], algoritimo['Previsão'])
    resultado_meansq = mean_squared_error(
        algoritimo['Fechamento'], algoritimo['Previsão'])
    print('\n')
    print(Panel(f"Teste do Erro absoluto médio [bold magenta]MAE[/bold magenta]\n\nMAE: [blue]{resultado_mean}[/blue]\nRMSE: [blue]{resultado_meansq}[/blue]",
          title="[bold]Auto ARIMA - Teste de precisão[/bold]", subtitle=f"{'[green]APROVADO[/green]' if (resultado_mean*2) > resultado_meansq else '[red]REPROVADO[/red]'}"))
    algoritimo2 = preparacao.teste_treinamento_prophet(dataframe)
    resultado_mean2 = mean_absolute_error(
        algoritimo2['Close'], algoritimo2['yhat'])
    resultado_meansq2 = mean_squared_error(
        algoritimo2['Close'], algoritimo2['yhat'])
    print('\n')
    print(Panel(f"Teste do Erro absoluto médio [bold magenta]MAE[/bold magenta]\n\nMAE: [blue]{resultado_mean2}[/blue]\nRMSE: [blue]{resultado_meansq2}[/blue]",
          title="[bold]Prophet - Teste de precisão[/bold]", subtitle=f"{'[green]APROVADO[/green]' if (resultado_mean2*2) > resultado_meansq2 else '[red]REPROVADO[/red]'}"))
