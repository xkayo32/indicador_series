# Importing the necessary libraries for the class to work.
import matplotlib.pyplot as plt
import pandas as pd
import scipy.stats as stats
from prophet import Prophet


class Preparacao:
    def __init__(self) -> None:
        """
        > The function `__init__` receives a dataframe and assigns it to the attribute `__dataframe`

        :param dataframe: The dataframe that will be used to create the series
        :type dataframe: pd.DataFrame
        """
        self.modelo_prophet = Prophet()

    def preparando_serie(self, dataframe: pd.DataFrame) -> pd.Series:
        """
        It returns a series with the closing price of the stock
        : return: A series with the closing price of the stock.
        """
        serie: pd.Series = dataframe['Close'].copy()
        serie.name = 'Fechamento'
        return serie

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

    def previsao_prophet(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        dataframe = self.__serie_to_dataframe_prophet(dataframe)
        modelo_prophet = Prophet()
        modelo_prophet.fit(dataframe)
        futuro = modelo_prophet.make_future_dataframe(periods=5)
        previsores = modelo_prophet.predict(futuro)
        df_previsores = previsores[[
            'ds', 'yhat', 'yhat_lower', 'yhat_upper', 'trend_lower', 'trend_upper']]
        df_previsores.columns = ['data', 'fechamento_previsto', 'minima_previsto',
                                 'maxima_previsto', 'minima_tendencia', 'maxima_tendencia']
        return df_previsores

    def join_daframe_prev(self, dataframe: pd.DataFrame, previsao: pd.DataFrame) -> pd.DataFrame:
        dataframe = dataframe['Close'].to_frame()
        dataframe = dataframe.reset_index()
        dataframe.columns = ['data', 'Close']
        previsao = previsao.merge(dataframe, how='left', on='data')
        return previsao

    def __serie_to_dataframe_prophet(self, dataframe: pd.DataFrame):
        dataframe = dataframe['Close'].to_frame()
        dataframe = dataframe.reset_index()
        dataframe.columns = ['ds', 'y']
        return dataframe
