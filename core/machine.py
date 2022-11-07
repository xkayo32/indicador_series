import pandas as pd
import scipy.stats as stats
from statsmodels.tsa.seasonal import DecomposeResult, seasonal_decompose


class Preparacao:
    def __init__(self, dataframe: pd.DataFrame) -> None:
        self.dataframe = dataframe
        self.serie = self.preparando_serie

    @property
    def preparando_serie(self) -> pd.DataFrame:
        return pd.DataFrame(index=pd.to_datetime(self.dataframe.index),
                            data=self.dataframe.Close.to_list(), columns=['Close'])

    # @property
    # def decompose_serie(self) -> DecomposeResult:
    #     return seasonal_decompose(self.preparando_serie)

    @property
    def teste_shapiro(self) -> tuple:
        return stats.shapiro(self.serie)

    @property
    def teste_ksmirnov(self) -> tuple:
        return stats.normaltest(self.serie)
