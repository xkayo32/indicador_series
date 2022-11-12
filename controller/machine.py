# Importing the necessary libraries for the class to work.
import math
from datetime import timedelta

import pandas as pd
import scipy.stats as stats
from pmdarima import auto_arima
from prophet import Prophet
from statsmodels.tsa.seasonal import DecomposeResult, seasonal_decompose


class Preparacao:
    def __init__(self) -> None:
        """
        > The function `__init__` receives a dataframe and assigns it to the attribute `__dataframe`

        :param dataframe: The dataframe that will be used to create the series
        :type dataframe: pd.DataFrame
        """
        self.modelo_prophet = Prophet()
        

    def preparando_serie(self,dataframe:pd.DataFrame) -> pd.Series:
        """
        It returns a series with the closing price of the stock
        : return: A series with the closing price of the stock.
        """
        serie: pd.Series = dataframe['Close'].copy()
        serie.name = 'Fechamento'
        return serie

    def decomposicao(self, serie: pd.Series) -> DecomposeResult:
        """
        It takes a pandas Series as input and returns a seasonal_decompose object

        :param serie: The time series you want to decompose
        :type serie: pd.Series
        :return: The decomposition of the series into trend, seasonal and residual components.
        """
        resultado = seasonal_decompose(serie, period=serie.shape[0] // 2)
        return resultado

    def teste_shapiro(self, serie) -> tuple:
        """
        It tests the null hypothesis that the data was drawn from a normal distribution

        :param serie: the series to be tested
        :return: The Shapiro-Wilk test tests the null hypothesis that the data was drawn from a normal
        distribution.
        """
        return stats.shapiro(serie)

    def teste_person(self, serie) -> tuple:
        """
        It tests the null hypothesis that a sample comes from a normal distribution

        :param serie: The data series to be tested
        :return: The test statistic and the p-value.
        """
        return stats.normaltest(serie)


    def previsao_prophet(self, dataframe:pd.DataFrame):
        dataframe = self.__serie_to_dataframe_prophet(dataframe)
        modelo_prophet = Prophet()
        modelo_prophet.fit(dataframe)
        futuro = modelo_prophet.make_future_dataframe(periods=8)
        previsores = modelo_prophet.predict(futuro)
        previsores = previsores[['ds','yhat', 'yhat_lower', 'yhat_upper']]
        previsores.columns = ['data','fechamento_previsto','minima_previsto','maxima_previsto']
        return previsores

    def join_daframe_prev(self,dataframe:pd.DataFrame,previsao:pd.DataFrame) -> pd.DataFrame:
        dataframe = dataframe['Close'].to_frame()
        dataframe = dataframe.reset_index()
        dataframe.columns = ['data','Close']
        previsao = previsao.merge(dataframe,how='left',on='data')
        return previsao


    def __serie_to_dataframe_prophet(self, dataframe: pd.DataFrame):
        dataframe = dataframe['Close'].to_frame()
        dataframe = dataframe.reset_index()
        dataframe.columns = ['ds', 'y']
        return dataframe

 