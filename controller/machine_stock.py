# Importing the necessary libraries for the class to work.
from dataclasses import dataclass

import pandas as pd
import scipy.stats as stats
from prophet import Prophet
from prophet.diagnostics import performance_metrics


class Preparacao:

    def __init__(self, dataframe) -> None:
        self.dataframe = dataframe
        self.serie = self.preparando_serie()

    def preparando_serie(self) -> pd.Series:
        """
        It returns a series with the closing price of the stock
        : return: A series with the closing price of the stock.
        """
        serie: pd.Series = self.dataframe['Close'].copy()
        serie.name = 'Fechamento'
        return serie

    def teste_shapiro(self) -> tuple:
        """
        It tests the null hypothesis that the data was drawn from a normal distribution

        :param serie: the series to be tested
        :return: The Shapiro-Wilk test tests the null hypothesis that the data was drawn from a normal
        distribution.
        """
        return stats.shapiro(self.serie)

    def teste_person(self) -> tuple:
        """
        It tests the null hypothesis that a sample comes from a normal distribution

        :param serie: The data series to be tested
        :return: The test statistic and the p-value.
        """
        return stats.normaltest(self.serie)

    def previsao_prophet(self) -> pd.DataFrame:
        modelo_prophet = Prophet()
        dataframe = self.__serie_to_dataframe_prophet()
        modelo_prophet.fit(dataframe)
        futuro = modelo_prophet.make_future_dataframe(periods=5)
        previsores = modelo_prophet.predict(futuro)
        return previsores

    def __previsao_tratada(self) -> pd.DataFrame:
        df_previsores = self.previsao_prophet()[[
            'ds', 'yhat', 'yhat_lower', 'yhat_upper', 'trend_lower', 'trend_upper']]
        df_previsores.columns = ['data', 'fechamento_previsto', 'minima_previsto',
                                 'maxima_previsto', 'minima_tendencia', 'maxima_tendencia']
        return df_previsores

    def join_daframe_prev(self) -> pd.DataFrame:
        dataframe = self.dataframe['Close'].to_frame()
        dataframe = dataframe.reset_index()
        dataframe.columns = ['data', 'Close']
        previsao = self.__previsao_tratada().merge(
            dataframe, how='left', on='data')
        previsao.to_csv('previsao.csv', index=False)
        return previsao

    def __serie_to_dataframe_prophet(self) -> pd.DataFrame:
        dataframe = self.dataframe['Close'].to_frame()
        dataframe = dataframe.reset_index()
        dataframe.columns = ['ds', 'y']
        return dataframe
