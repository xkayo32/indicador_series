""" Kayo Carvalho Fernandes
"""

# Importing the datetime module, the pandas module and the yfinance module.
from datetime import datetime, timedelta

import pandas as pd
import requests_cache
import yfinance as yf

from controller.machine import Preparacao


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
                                                                start=inicio, interval=self.intervalo)],session=self.session)
                return yf_ativo
            else:
                return yf.download(self.ativo, end=self.data_final,
                                   start=self.data_inicial, interval=self.intervalo,session=self.session)
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

    def infor_ativo(self):
        return yf.Ticker(self.ativo)


if __name__ == '__main__':
    ativo = AtivoController('PETR4.SA', '2022-06-01', '2022-11-08', '1d')
    preparacao = Preparacao(ativo.base_dados)
