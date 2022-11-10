""" Kayo Carvalho Fernandes
"""

import warnings
from datetime import datetime, timedelta

import pandas as pd
import requests_cache
import yfinance as yf
from machine import Preparacao
from rich import print
from rich.console import Console
from rich.panel import Panel
from sklearn.metrics import mean_absolute_error, mean_squared_error

warnings.filterwarnings("ignore")


# > This class is used to get data from the Alpha Vantage API.
class AtivoController(Preparacao):
    def __init__(self, ativo: str, data_inicial: str, data_final: str, intervalo: str = '1d') -> None:
        """
        A constructor of the class.

        :param ativo: The stock symbol
        :type ativo: str
        :param data_inicial: The start date of the data you want to download
        :type data_inicial: str
        :param data_final: The end date for the data series
        :type data_final: str
        :param intervalo: The interval of time between each data point. valiWd intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        :type intervalo: str 
        """
        self.session = requests_cache.CachedSession('yfinance.cache')
        self.session.headers['User-agent'] = 'my-prgram/1.0'
        self.data_inicial = data_inicial
        self.data_final = data_final
        self.ativo = ativo
        self.intervalo = intervalo
        self.base_dados: pd.DataFrame = self.__download_ativos()
        super().__init__(self.base_dados)

    @property
    def ativo(self):
        return self.__ativo

    @ativo.setter
    def ativo(self, valor):
        self.__ativo = valor

    @property
    def data_inicial(self) -> str:
        """
        It returns the value of the variable __data_inicial
        :return: The data_inicial attribute.
        """
        return self.__data_inicial

    @data_inicial.setter
    def data_inicial(self, valor: str | datetime) -> None:
        """
        If the value passed to the function is a string, convert it to a datetime object and then convert it
        back to a string in the format 'YYYY-MM-DD'. If the value passed to the function is a datetime
        object, just convert it to a string in the format 'YYYY-MM-DD'

        :param valor: str | datetime
        :type valor: str | datetime
        """
        if isinstance(valor, str):
            self.__data_inicial = datetime.strptime(
                valor, '%Y-%m-%d').strftime('%Y-%m-%d')
        else:
            self.__data_inicial = valor.strftime('%Y-%m-%d')

    @property
    def data_final(self) -> str:
        """
        It returns the value of the variable __data_final
        :return: The data final is being returned.
        """
        return self.__data_final

    @data_final.setter
    def data_final(self, valor: str | datetime):
        """
        If the value passed to the function is a string, convert it to a datetime object and then convert it
        back to a string in the format 'YYYY-MM-DD'. If the value passed to the function is a datetime
        object, just convert it to a string in the format 'YYYY-MM-DD'

        :param valor: The value to be assigned to the attribute
        :type valor: str | datetime
        """
        if isinstance(valor, str):
            self.__data_final = (datetime.strptime(
                valor, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
        else:
            self.__data_final = (valor + timedelta(days=1)
                                 ).strftime('%Y-%m-%d')

    def __dias_intervalo(self, data_inicial: str, data_final: str) -> int:
        dias = (datetime.strptime(data_inicial, '%Y-%m-%d') -
                datetime.strptime(data_final, '%Y-%m-%d')).days
        return abs(dias)

    def __download_ativos(self) -> pd.DataFrame:
        try:
            if self.intervalo in ['1m', '2m', '5m', '15m', '30m'] and self.__dias_intervalo(self.data_inicial, self.data_final) > 7:
                datas = self.__lista_data()
                yf_ativo = pd.DataFrame()
                for inicio, fim in datas:
                    yf_ativo = pd.concat([yf_ativo, yf.download(self.ativo, end=fim,
                                                                start=inicio, interval=self.intervalo)], session=self.session)
                return yf_ativo
            else:
                return yf.download(self.ativo, end=self.data_final,
                                   start=self.data_inicial, interval=self.intervalo, session=self.session)
        except:
            return pd.DataFrame()

    def __lista_data(self):
        datas = []
        while (not datas) or (not self.data_final in datas[-1]):
            if not datas:
                dias_intervalo = self.__dias_intervalo(
                    self.data_inicial, self.data_final)
                dias_reduzidos = 6 if not dias_intervalo <= 6 else dias_intervalo
                datas.append(
                    (self.data_inicial, self.__adicionar_remover_dias(
                        self.data_inicial, '+', dias_reduzidos))
                )
            else:
                dia_apos = self.__adicionar_remover_dias(datas[-1][1], '+', 1)
                dias_intervalo = self.__dias_intervalo(
                    dia_apos, self.data_final)
                dias_reduzidos = 6 if not dias_intervalo <= 6 else dias_intervalo
                datas.append((dia_apos, self.__adicionar_remover_dias(
                    dia_apos, '+', dias_reduzidos)))
        return datas

    @staticmethod
    def __adicionar_remover_dias(data: str, operador: str, dias: int) -> str:
        match operador:
            case '-':
                return (datetime.strptime(data, '%Y-%m-%d') - timedelta(days=dias)).strftime('%Y-%m-%d')
            case '+':
                return (datetime.strptime(data, '%Y-%m-%d') + timedelta(days=dias)).strftime('%Y-%m-%d')
            case _:
                return ''

    @property
    def infor_ativo(self):
        return yf.Ticker(self.ativo)


if __name__ == '__main__':
    console = Console()
    acao = 'PETR4.SA'
    ativo = AtivoController(acao, '2022-01-01', '2022-11-09', '1d')
    preparacao = Preparacao(ativo.base_dados)
    serie = preparacao.serie
    # tabela = Table(title=f'{ativo.infor_ativo.info["shortName"]}')
    # tabela.add_column(f'{serie.index.name}',
    #                   justify='center', style='cyan')
    # tabela.add_column(f'{serie.name}', justify='center',
    #                   style='magenta')
    # for i, v in serie.items():
    #     tabela.add_row(str(i), str(v))
    if serie.size < 30:
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
    algoritimo = preparacao.teste_treinamento_auto_arima()
    resultado_mean = mean_absolute_error(
        algoritimo['Fechamento'], algoritimo['Previsão'])
    resultado_meansq = mean_squared_error(
        algoritimo['Fechamento'], algoritimo['Previsão'])
    print('\n')
    print(Panel(f"Teste do Erro absoluto médio [bold magenta]MAE[/bold magenta]\n\nMAE: [blue]{resultado_mean}[/blue]\nRMSE: [blue]{resultado_meansq}[/blue]",
          title="[bold]Auto ARIMA - Teste de precisão[/bold]", subtitle=f"{'[green]APROVADO[/green]' if resultado_mean*2 < resultado_meansq else '[red]REPROVADO[/red]'}"))
    algoritimo2 = preparacao.teste_treinamento_prophet()
    resultado_mean2 = mean_absolute_error(
        algoritimo2['y'], algoritimo2['yhat'])
    resultado_meansq2 = mean_squared_error(
        algoritimo2['y'], algoritimo2['yhat'])
    print('\n')
    print(Panel(f"Teste do Erro absoluto médio [bold magenta]MAE[/bold magenta]\n\nMAE: [blue]{resultado_mean2}[/blue]\nRMSE: [blue]{resultado_meansq2}[/blue]",
          title="[bold]Prophet - Teste de precisão[/bold]", subtitle=f"{'[green]APROVADO[/green]' if resultado_mean2*2 < resultado_meansq2 else '[red]REPROVADO[/red]'}"))
