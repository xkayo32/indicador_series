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

    def auto_arima_teste(self, serie: pd.Series):
        """
        It will return the best ARIMA model for the given time series, based on the AIC criterion

        :param serie: The time series you want to forecast
        :type serie: pd.Series
        :return: A tuple with the best model and the best order.
        """
        return auto_arima(serie, suppress_warnings=True,
                          error_action='ignore')

    def __previsao_auto_arima(self, resultado, base_treino: pd.Series, dias: int = 4, base_teste=None):
        """
        It takes the result of the auto_arima function, the training data, the number of days to predict,
        and the test data, and returns a dataframe with the predicted values and the actual values

        :param resultado: the model object
        :param base_treino: The training data
        :type base_treino: pd.Series
        :param dias: The number of days to predict, defaults to 4
        :type dias: int (optional)
        :param base_teste: The test dataframe
        :return: a dataframe with the forecasted values and the real values.
        """
        dados = resultado.predict(dias)
        if base_teste is None:
            dados.index = pd.date_range(start=(base_treino.index[-1] + timedelta(
                days=1)), end=base_treino.index[-1] + timedelta(days=dias))
        else:
            dados.index = base_teste.index
        dataframe = pd.DataFrame(data=dados, columns=['Previsão'])
        dataframe = dataframe.join(base_teste)
        return dataframe

    def teste_treinamento_auto_arima(self,serie: pd.Series):
        """
        It takes a series, splits it into training and testing sets, and then uses the training set to fit
        an ARIMA model. The model is then used to make predictions on the test set
        :return: The result of the test is being returned.
        """
        tamanho_base = math.ceil(serie.shape[0] * 0.80)
        base_treino = serie[:tamanho_base]
        base_teste = serie[tamanho_base:]
        resultado = self.auto_arima_teste(base_treino)
        return self.__previsao_auto_arima(resultado, base_treino, base_teste=base_teste, dias=base_teste.shape[0])

    def previsao_prophet(self, dataframe:pd.DataFrame):
        dataframe = self.__serie_to_dataframe_prophet(dataframe)
        modelo_prophet = Prophet()
        modelo_prophet.fit(dataframe)
        futuro = modelo_prophet.make_future_dataframe(periods=8)
        previsores = modelo_prophet.predict(futuro)
        previsores = previsores[['ds','yhat', 'yhat_lower', 'yhat_upper']]
        previsores.columns = ['data','fechamento_previsto','minima_previsto','maxima_previsto']
        return previsores

    def teste_treinamento_prophet(self,dataframe: pd.DataFrame):
        """
        It takes a series, splits it into training and testing sets, and then uses the training set to fit
        an ARIMA model. The model is then used to make predictions on the test set
        :return: The result of the test is being returned.
        """
        base_dados_prophet = self.__serie_to_dataframe_prophet(dataframe)
        tamanho_base = math.ceil(base_dados_prophet.shape[0] * 0.80)
        base_treino = base_dados_prophet[:tamanho_base]
        base_teste = dataframe[tamanho_base:]
        self.modelo_prophet.fit(base_treino)
        return self.__previsao_prophet(base_teste=base_teste, dias=base_teste.shape[0])

    def __previsao_prophet(self, base_teste, dias=4):
        futuro = self.modelo_prophet.make_future_dataframe(periods=dias)
        previsores = self.modelo_prophet.predict(futuro)
        previsores = previsores.tail(dias).set_index('ds')
        previsores = previsores.join(base_teste)
        return previsores[['Close','yhat', 'yhat_lower', 'yhat_upper']].dropna()

    def __serie_to_dataframe_prophet(self, dataframe: pd.DataFrame):
        dataframe = dataframe['Close'].to_frame()
        dataframe = dataframe.reset_index()
        dataframe.columns = ['ds', 'y']
        return dataframe

 