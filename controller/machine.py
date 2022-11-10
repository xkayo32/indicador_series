import math
from datetime import timedelta

import pandas as pd
import scipy.stats as stats
import statsmodels.tsa.arima.model as stats_model
from pmdarima import auto_arima
from statsmodels.tsa.seasonal import DecomposeResult, seasonal_decompose


class Preparacao:
    def __init__(self, dataframe: pd.DataFrame) -> None:
        self.__dataframe = dataframe
        self.serie = self.preparando_serie

    @property
    def preparando_serie(self) -> pd.Series:
        return self.__dataframe['Close']

    def decomposicao(self, serie: pd.Series) -> DecomposeResult:
        return seasonal_decompose(serie, period=len(serie) // 2)

    def teste_shapiro(self, serie) -> tuple:
        return stats.shapiro(serie)

    def teste_person(self, dataframe) -> tuple:
        w, p = stats.normaltest(dataframe)
        return w, p

    def arima_teste(self, serie, p: int = 0, d: int = 0, q: int = 0):
        modelo = stats_model.ARIMA(serie, order=(p, d, q))
        self.resultado = modelo.fit()
        return self.resultado

    def auto_arima_teste(self, serie: pd.Series):
        return auto_arima(serie, suppress_warnings=True,
                          error_action='ignore')

    def previsao_arima(self, dias: int = 4):
        return self.resultado.forecast(dias)

    def previsao_auto_arima(self, resultado, base_treino: pd.Series, dias: int = 4, base_teste=None):
        dados = resultado.predict(n_periods=dias)
        if base_teste is None:
            dados.index = pd.date_range(start=(base_treino.index[-1] + timedelta(
                days=1)), end=base_treino.index[-1] + timedelta(days=dias))
        else:
            dados.index = base_teste.index
        return pd.DataFrame(data=dados, columns=['Previsão'])

    def teste_treinamento_auto_arima(self):
        tamanho_base = math.ceil(self.serie.size * 0.7)
        base_treino = self.serie[:tamanho_base]
        base_teste = self.serie[tamanho_base:]
        resultado = self.auto_arima_teste(base_treino)
        return self.previsao_auto_arima(resultado, base_treino, base_teste=base_teste, dias=base_teste.size)
