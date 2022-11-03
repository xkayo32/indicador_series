""" Kayo Carvalho Fernandes
"""

# Importing the datetime module, the pandas module and the yfinance module.
from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf


# > This class is used to get data from the Alpha Vantage API.
class AtivoController(object):
    def __init__(self, ativo: str, data_inicial: str, data_final: str, intervalo: str = '1d') -> None:
        """
        A constructor of the class.

        :param ativo: The stock symbol
        :type ativo: str
        :param data_inicial: The start date of the data you want to download
        :type data_inicial: str
        :param data_final: The end date for the data series
        :type data_final: str
        :param intervalo: The interval of time between each data point. valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        :type intervalo: str 
        """
        self.data_inicial = data_inicial
        self.data_final = data_final
        self.ativo = ativo
        self.intervalo = intervalo

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
            self.__data_inicial = valor

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
            self.__data_final = datetime.strptime(
                valor, '%Y-%m-%d').strftime('%Y-%m-%d')
        else:
            self.__data_final = valor

    def buscar_ativo(self,) -> pd.DataFrame:
        """
        It downloads the stock data from Yahoo Finance, and returns a pandas dataframe
        :return: A dataframe with the stock data.
        """
        # try:
        yf_ativo = self.download_ativos()

        # except Exception as exception:
        #     print(exception)
        #     yf_ativo = pd.DataFrame([])

        # finally:
        return yf_ativo

    def __dias_intervalo(self, data_inicial, data_final):
        dias = (datetime.strptime(data_inicial, '%Y-%m-%d') -
                datetime.strptime(data_final, '%Y-%m-%d')).days
        return abs(dias)

    def download_ativos(self):
        if self.intervalo in ['1m', '2m', '5m', '15m', '30m'] and self.__dias_intervalo(self.data_inicial, self.data_final) > 7 and self.__check_range_data():
            datas = self.__lista_data()
            yf_ativo = pd.DataFrame()
            for inicio, fim in datas:
                yf_ativo = pd.concat([yf_ativo, yf.download(self.ativo, end=fim,
                                                            start=inicio, interval=self.intervalo)])
            return yf_ativo
        else:
            return yf.download(self.ativo, end=self.data_final,
                               start=self.data_inicial, interval=self.intervalo)

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

    def __adicionar_remover_dias(self, data: str, operador: str, dias: int) -> str | bool:
        match operador:
            case '-':
                return (datetime.strptime(data, '%Y-%m-%d') - timedelta(days=dias)).strftime('%Y-%m-%d')
            case '+':
                return (datetime.strptime(data, '%Y-%m-%d') + timedelta(days=dias)).strftime('%Y-%m-%d')
            case _:
                return False

    def __check_range_data(self):
        match self.intervalo:
            case '1m':
                return (datetime.now() - datetime.strptime(self.data_inicial, '%Y-%m-%d')).days <= 30
            case '2m' | '5m' | '15m' | '30m':
                return (datetime.now() - datetime.strptime(self.data_inicial, '%Y-%m-%d')).days <= 30
    # def __buscar_periodo(self):
    #     match self.intervalo:
    #         case '1m':


if __name__ == '__main__':
    ativo = AtivoController('GOOG', '2022-10-15', '2022-11-03', '1m')
    print(ativo.buscar_ativo())
    # print(yf.download('GOOG', start='2022-10-28',
    #                   end='2022-11-03', interval='1m'))
