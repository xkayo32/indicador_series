# Importing the necessary libraries for the class to work.
import math
from datetime import timedelta

import pandas as pd
import scipy.stats as stats
from pmdarima import auto_arima
from prophet import Prophet
from statsmodels.tsa.seasonal import DecomposeResult, seasonal_decompose


class Preparacao:
    def __init__(self, dataframe: pd.DataFrame) -> None:
        """
        > The function `__init__` receives a dataframe and assigns it to the attribute `__dataframe`

        :param dataframe: The dataframe that will be used to create the series
        :type dataframe: pd.DataFrame
        """
        self.__dataframe = dataframe
        self.serie = self.preparando_serie
        self.modelo_prophet = Prophet()

    @property
    def preparando_serie(self) -> pd.Series:
        """
        It returns a series with the closing price of the stock
        : return: A series with the closing price of the stock.
        """
        serie: pd.Series = self.__dataframe['Close']
        serie.name = 'Fechamento'
        return serie

    def decomposicao(self, serie: pd.Series) -> DecomposeResult:
        """
        It takes a pandas Series as input and returns a seasonal_decompose object

        :param serie: The time series you want to decompose
        :type serie: pd.Series
        :return: The decomposition of the series into trend, seasonal and residual components.
        """
        resultado = seasonal_decompose(serie, period=serie.size // 2)
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

    def teste_treinamento_auto_arima(self):
        """
        It takes a series, splits it into training and testing sets, and then uses the training set to fit
        an ARIMA model. The model is then used to make predictions on the test set
        :return: The result of the test is being returned.
        """
        tamanho_base = math.ceil(self.serie.size * 0.80)
        base_treino = self.serie[:tamanho_base]
        base_teste = self.serie[tamanho_base:]
        resultado = self.auto_arima_teste(base_treino)
        return self.__previsao_auto_arima(resultado, base_treino, base_teste=base_teste, dias=base_teste.size)

    def teste_treinamento_prophet(self):
        """
        It takes a series, splits it into training and testing sets, and then uses the training set to fit
        an ARIMA model. The model is then used to make predictions on the test set
        :return: The result of the test is being returned.
        """
        base_dados_prophet = self.__serie_to_dataframe_prophet(self.serie)
        tamanho_base = math.ceil(base_dados_prophet.size * 0.80)
        base_treino = base_dados_prophet[:tamanho_base]
        base_teste = base_dados_prophet[tamanho_base:]
        self.prophet_teste(base_treino)
        return self.__previsao_prophet(base_teste=base_teste, dias=base_teste.size)

    def __previsao_prophet(self, base_teste, dias=4):
        futuro = self.modelo_prophet.make_future_dataframe(periods=dias)
        previsores = self.modelo_prophet.predict(futuro)
        print(previsores)
        return previsores

    def __serie_to_dataframe_prophet(self, serie: pd.DataFrame):
        dataframe: pd.DataFrame = serie.to_frame()
        dataframe.reset_index(inplace=True)
        dataframe.columns = ['ds', 'y']
        return dataframe

    def prophet_teste(self, dataframe: pd.DataFrame):
        return self.modelo_prophet.fit(dataframe)
