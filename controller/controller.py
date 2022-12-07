""" Kayo Carvalho Fernandes
"""
import logging
import warnings
from dataclasses import dataclass
from datetime import datetime, timedelta

import pandas as pd
import plotly.graph_objects as go
import requests_cache
import yfinance as yf

from controller.machine_stock import Preparacao

warnings.filterwarnings("ignore")
logging.disable()
session = requests_cache.CachedSession('yfinance.cache')
session.headers['User-agent'] = 'my-program/1.0'

# > This class is used to get data from the Alpha Vantage API.


@dataclass
class AtivoController(Preparacao):
    ativo: str
    data_inicial: str
    data_final: str

    def __post_init__(self) -> None:
        self.base_dados = self.__get_base_dados()
        Preparacao.__init__(self, self.base_dados)
        self.previsao = self.base_previsao()

    @property
    def data_final(self) -> str:
        return self._data_final

    @data_final.setter
    def data_final(self, value: str) -> None:
        self._data_final = (datetime.strptime(
            value, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')

    @property
    def infor_ativo(self) -> float:
        return yf.Ticker(self.ativo, session=session)

    def base_previsao(self) -> pd.DataFrame:
        return self.join_daframe_prev()

    def tendencia(self, base_previsao: bool = True) -> dict:
        match base_previsao:
            case True:
                previsao = self.previsao.copy()
                previsao = previsao.dropna()
                coluna = 'maxima_tendencia'
            case False:
                previsao = self.base_dados.copy()
                coluna = 'Close'

        if previsao[coluna].iloc[0] < previsao[coluna].iloc[-1]:
            if previsao[coluna].mean() < previsao[coluna].iloc[-1]:
                return {'tendencia': 'Forte Alta', 'fibonacci': self.__fibonacci_ret('alta', previsao, coluna)}
            else:
                return {'tendencia': 'Alta', 'fibonacci': self.__fibonacci_ret('alta', previsao, coluna)}
        else:
            if previsao[coluna].mean() > previsao[coluna].iloc[-1]:
                return {'tendencia': 'Forte Baixa', 'fibonacci': self.__fibonacci_ret('baixa', previsao, coluna)}
            else:
                return {'tendencia': 'Baixa', 'fibonacci': self.__fibonacci_ret('baixa', previsao, coluna)}

    def grafico_candle(self) -> go.Figure:
        candle = go.Figure(data=[go.Candlestick(x=self.base_dados.index, open=self.base_dados['Open'],
                                                high=self.base_dados['High'], low=self.base_dados['Low'], close=self.base_dados['Close'], name='Candle')], layout=go.Layout(title='Candle'))
        candle.update_layout(xaxis_rangeslider_visible=False)
        for grau, valor in self.tendencia(base_previsao=False)['fibonacci'].items():
            candle.add_hline(y=valor, line_dash='dash', annotation_text=grau)
        return candle

    def grafico_tendencia(self) -> go.Figure:
        previsao = self.previsao.copy()
        previsao = previsao.dropna()
        fibo = go.Figure(data=[go.Scatter(
            x=previsao.data, y=previsao['maxima_tendencia'], name='Tendencia')], layout=go.Layout(title='Tendencia'))
        for grau in self.tendencia()['fibonacci']:
            fibo.add_hline(y=self.tendencia()[
                           'fibonacci'][grau], line_dash='dash', annotation_text=grau)
        return fibo

    def __fibonacci_ret(self, tendencia: str, previsao: pd.DataFrame, coluna: str) -> dict[float] | bool:
        match tendencia:
            case 'alta':
                return self.__calc_fibonacci_alta(previsao, coluna)
            case 'baixa':
                return self.__calc_fibonacci_baixa(previsao, coluna)
            case _:
                return False

    def __calc_fibonacci_alta(self, previsao: pd.DataFrame, coluna: str) -> dict:
        maxima = previsao[coluna].max()
        minima = previsao[coluna].min()
        diferenca = maxima - minima
        return {'100': minima, '61.8': maxima - (diferenca * 0.618), '50': maxima - (diferenca * 0.5), '38.2': maxima - (diferenca * 0.382), '0': maxima}

    def __calc_fibonacci_baixa(self, previsao: pd.DataFrame, coluna: str) -> dict:
        maxima = previsao[coluna].max()
        minima = previsao[coluna].min()
        diferenca = maxima - minima
        return {'100': maxima, '61.8': minima + (diferenca * 0.618), '50': minima + (diferenca * 0.5), '38.2': minima + (diferenca * 0.382), '0': minima}

    def __get_base_dados(self) -> pd.DataFrame:
        return yf.download(self.ativo, start=self.data_inicial, end=self.data_final, progress=False, session=session)
