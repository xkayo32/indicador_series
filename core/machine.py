import numpy as np
import pandas as pd
import scipy.stats as stats
from statsmodels.tsa.seasonal import seasonal_decompose


class Preparacao:
    def __init__(self, dataframe: pd.DataFrame) -> None:
        self.dataframe = dataframe
        self.serie = self.preparando_serie

    @property
    def preparando_serie(self) -> pd.Series:
        return self.dataframe['Close'].copy()
        # return pd.Series(index=pd.to_datetime(self.dataframe.index), data=self.dataframe.Close.to_list())

    @property
    def preparando_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(index=self.dataframe.index, data=self.normalizacao_log.tolist(), columns=['Close'])

    @property
    def normalizacao_log(self):
        return np.log(self.serie.copy())

    @property
    def decomposicao(self):
        return seasonal_decompose(self.serie, period=self.serie.size // 2)

    def teste_shapiro(self, serie) -> tuple:
        return stats.shapiro(serie)

    def teste_person(self, dataframe) -> tuple:
        return stats.normaltest(pd.DataFrame(index=dataframe.index, data=dataframe.Close.to_list(), columns=['Close']))
