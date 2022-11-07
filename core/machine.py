import pandas as pd
import scipy.stats as stats
from statsmodels.tsa.seasonal import DecomposeResult, seasonal_decompose


class Preparacao:
    def __init__(self, dataframe: pd.DataFrame) -> None:
        self.dataframe = dataframe
        self.serie = self.preparando_serie

    @property
    def preparando_serie(self) -> pd.Series:
        return pd.Series(index=self.dataframe.index,
                         data=self.dataframe.Close.to_list())

    @property
    def decompose_serie(self) -> DecomposeResult:
        return seasonal_decompose(self.serie, period=None)

    @property
    def teste_shapiro(self) -> tuple:
        return stats.shapiro(self.serie)
