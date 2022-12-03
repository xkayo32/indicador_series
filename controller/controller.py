""" Kayo Carvalho Fernandes
"""

import logging
import warnings
from dataclasses import dataclass

import pandas as pd
import requests_cache
import yfinance as yf
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error

from controller.machine_stock import Preparacao

warnings.filterwarnings("ignore")
logging.disable()
session = requests_cache.CachedSession('yfinance.cache')
session.headers['User-agent'] = 'my-program/1.0'

# > This class is used to get data from the Alpha Vantage API.


@dataclass
class AtivoController(Preparacao):
    __ativo: str = 'PETR4.SA'
    __data_inicial: str = '2020-01-01'
    __data_final: str = '2021-01-01'

    def __post_init__(self) -> None:
        self.base_dados = self.__get_base_dados()

    def __get_base_dados(self) -> pd.DataFrame:
        return yf.download(self.__ativo, start=self.__data_inicial, end=self.__data_final, progress=False, session=session)

    @property
    def infor_ativo(self) -> float:
        return yf.Ticker(self.__ativo, session=session)

    def __preparando_previsao(self) -> pd.DataFrame:
        return self.previsao_prophet(self.base_dados)

    @property
    def base_previsao(self) -> pd.DataFrame:
        return self.join_daframe_prev(self.base_dados, self.__preparando_previsao())

    def tendencia(self, previsao: pd.DataFrame) -> dict:
        if previsao['maxima_tendencia'].iloc[0] > previsao['minima_tendencia'].iloc[-1]:
            if previsao['maxima_tendencia'].mean() < previsao['minima_tendencia'].iloc[-1]:
                return {'tendencia': 'Forte Alta', 'fibonacci': self.__fibonacci_ret('alta', previsao)}
            else:
                return {'tendencia': 'Alta', 'fibonacci': self.__fibonacci_ret('alta', previsao)}
        else:
            if previsao['maxima_tendencia'].mean() > previsao['minima_tendencia'].iloc[-1]:
                return {'tendencia': 'Forte Baixa', 'fibonacci': self.__fibonacci_ret('baixa', previsao)}
            else:
                return {'tendencia': 'Baixa', 'fibonacci': self.__fibonacci_ret('baixa', previsao)}

    def __fibonacci_ret(self, tendencia: str, dados: pd.DataFrame) -> dict[float] | bool:
        match tendencia:
            case 'alta':
                return self.__calc_fibonacci_alta(dados)
            case 'baixa':
                return self.__calc_fibonacci_baixa(dados)
            case _:
                return False

    def __calc_fibonacci_alta(self, dados: pd.DataFrame) -> dict:
        maxima = dados['maxima_tendencia'].max()
        minima = dados['maxima_tendencia'].min()
        diferenca = maxima - minima
        return {'100': minima, '61.8': maxima - (diferenca * 0.618), '50': maxima - (diferenca * 0.5), '38.2': maxima - (diferenca * 0.382), '0': maxima}

    def __calc_fibonacci_baixa(self, dados: pd.DataFrame) -> dict:
        maxima = dados['minima_tendencia'].max()
        minima = dados['minima_tendencia'].min()
        diferenca = maxima - minima
        return {'100': maxima, '61.8': minima + (diferenca * 0.618), '50': minima + (diferenca * 0.5), '38.2': minima + (diferenca * 0.382), '0': minima}


if __name__ == '__main__':
    console = Console()
    acao = 'EURUSD=X'
    preparacao = Preparacao()
    ticker = yf.Ticker(acao, session=session)
    dataframe = yf.download(acao, start='2022-09-01', end='2022-11-30',
                            interval='1d', session=session, timeout=2)
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
    algoritimo2_dataframe = preparacao.join_daframe_prev(
        dataframe, algoritimo2)
    resultado_mean2 = mean_absolute_error(
        algoritimo2_dataframe['Close'][:dataframe.shape[0]], algoritimo2_dataframe['fechamento_previsto'][:dataframe.shape[0]])
    resultado_meansq2 = mean_absolute_percentage_error(
        algoritimo2_dataframe['Close'][:dataframe.shape[0]], algoritimo2_dataframe['fechamento_previsto'][:dataframe.shape[0]])
    print('\n')
    print(Panel(f"Teste do Erro absoluto médio [bold magenta]MAE[/bold magenta]\n\nMAE: [blue]{resultado_mean2}[/blue]\nMAPE: [blue]{resultado_meansq2}[/blue]",
          title="[bold]Prophet - Teste de precisão[/bold]", subtitle=f"{'[green]APROVADO[/green]' if resultado_mean2 < 3 else '[red]REPROVADO[/red]'}"))
    table = Table('Data', 'Fechamento previsto', 'Fechamento Real',
                  'Mínima previsto', 'Máxima previsto', title=f"Previsão dos preços da {acao}")
    for i, x in algoritimo2_dataframe.tail(6).iterrows():
        table.add_row(str(x.data), str(x.fechamento_previsto), str(
            x.Close), str(x.minima_previsto), str(x.maxima_previsto))
    console = Console()
    console.print(table)
