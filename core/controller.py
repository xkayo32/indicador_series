from datetime import datetime

import pandas as pd
import yfinance as yf


class AtivoController(object):
    def __init__(self, ativo: str, data_inicial: str, data_final: str, intervalo: str) -> None:
        self.data_inicial = data_inicial
        self.data_final = data_final
        self.ativo = ativo
        self.intervalo = intervalo

    @property
    def data_inicial(self):
        return self.__data_inicial

    @data_inicial.setter
    def data_inicial(self, valor: str|datetime):
        if isinstance(valor,str):
            self.__data_inicial = datetime.strptime(
                valor, '%Y-%m-%d').strftime('%Y-%m-%d')
        else:
            self.__data_inicial = valor

    @property
    def data_final(self):
        return self.__data_final

    @data_final.setter
    def data_final(self, valor: str|datetime):
        if isinstance(valor,str):
            self.__data_final = datetime.strptime(
                valor, '%Y-%m-%d').strftime('%Y-%m-%d')
        else:
            self.__data_final = valor

    def buscar_ativo(self) -> pd.DataFrame:
        yf_ativo = yf.download(self.ativo, end=self.data_final,
                               start=self.data_inicial, interval=self.intervalo)
        return yf_ativo
