"""main.py"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import scipy.stats as stats

from core import st
from core.controller import AtivoController
from core.machine import Preparacao
from core.validacao import Validacao


class Programa(Validacao):
    def __init__(self) -> None:
        super().__init__()
        self.st = st
        self.st.set_page_config(page_title='Sistema de recomendação', layout='wide',
                                page_icon='📈', initial_sidebar_state="auto", menu_items=None)
        self.main()

    def body_lateral(self) -> None:
        self.st.sidebar.header('Painel de configuração')
        self.acao = self.st.sidebar.text_input(
            f'Nome da ação', help='Link dos ativos da IBOV https://finance.yahoo.com/quote/%5EBVSP/components?p=%5EBVSP', placeholder='VALE5.SA', key='ativo_1')
        self.intervalo = self.__intervalos()
        self.data_inicial, self.data_final = self.__datas(self.intervalo)

    def body(self) -> None:
        self.st.title('Previsão de séries temporais 📈')
        if self.__validacao_campos():
            self.acao_controller = AtivoController(
                self.acao, self.data_inicial, self.data_final, self.intervalo)
            dados_carregado = self.acao_controller.download_ativos()
            if dados_carregado.size:  # type: ignore
                preparacao = Preparacao(dados_carregado)
                with self.st.expander('Gráfico em candlestick'):
                    self.grafico_candlestick(dados_carregado)
                with self.st.expander('Gráfico Histograma'):
                    self.grafico_qqplot(preparacao.serie)
                col1, col2, col3, col4, col5 = self.st.columns(5)
                with col1:
                    self.st.write('Preço atual')
                    self.st.write(dados_carregado['Close'].iloc[-1])
                with col2:
                    self.st.write('Mediana do período')
                    self.st.write(dados_carregado['Close'].median())
                with col3:
                    self.st.write('Taxa retorno do período')
                    self.st.write(round(np.log(
                        dados_carregado['Close'].iloc[1] / dados_carregado['Close'].iloc[-1]) * 100, 2))
                with col4:
                    self.st.write('Taxa de retorno intervalo')
                    self.st.write(round(np.log(
                        dados_carregado['Close'].iloc[-1] / dados_carregado['Close'].iloc[-2])*100, 2))
                with col5:
                    self.st.write('Coeficiente de variação')
                    self.st.write()
                if dados_carregado.size < 30:
                    self.st.header('Teste de shapiro')
                    col10, col11 = self.st.columns(2)
                    with col10:
                        self.st.write(f'Estatíca do teste: ',
                                      preparacao.teste_shapiro[0])
                    with col11:
                        self.st.write(
                            f'p-valor: ', preparacao.teste_shapiro[1])

                    if preparacao.teste_shapiro[1] > 0.05:
                        self.st.success('É uma distribuição normal')
                    else:
                        self.st.error('Não é uma distribuição normal')
                else:
                    self.st.header('Teste de Kolmogorov-Smirnov')
                    col20, col21 = self.st.columns(2)
                    with col20:
                        self.st.write(
                            'p-valor: ',
                            preparacao.teste_ksmirnov[1][0])
                    if preparacao.teste_ksmirnov[1][0] > 0.05:
                        self.st.success('É uma distribuição normal')
                    else:
                        self.st.error('Não é uma distribuição normal')
            else:
                st.warning('Dados não encontrados!')

    def grafico_candlestick(self, dataframe: pd.DataFrame) -> None:
        range_lines = self.st.checkbox('Ranges Lider')
        fig = go.Figure(data=[go.Candlestick(x=dataframe.index, open=dataframe['Open'],
                                             high=dataframe['High'], low=dataframe['Low'], close=dataframe['Close'])])
        fig.update_layout(xaxis_rangeslider_visible=range_lines)
        self.st.plotly_chart(fig, use_container_width=True)

    # def grafico_decompose(self, serie: pd.DataFrame) -> None:
    #     fig = go.Figure(
    #         data=[go.Scatter(x=serie.index, y=serie)])
    #     self.st.plotly_chart(fig, use_container_width=True)

    def grafico_qqplot(self, serie: pd.DataFrame):
        fig = go.Figure(
            data=[go.Histogram(x=serie.Close)])
        self.st.plotly_chart(fig, use_container_width=True)

    def main(self) -> None:
        self.body_lateral()
        self.body()

    def __datas(self, intervalo: str) -> list:
        max_date, min_date = self.min_max_data_inicial(intervalo)
        data_inicial = self.st.sidebar.date_input(
            'Data Inicial', min_value=min_date, max_value=max_date, key='data_inicial1')
        data_final = self.st.sidebar.date_input(
            'Data Final', min_value=data_inicial, max_value=max_date, key='data_final1', value=max_date)  # type: ignore
        return [data_inicial, data_final]

    def __intervalos(self) -> str:
        intervalo = self.st.sidebar.select_slider('Intervalo', [
            '1m', '2m', '5m', '15m', '30m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'], value='1d', key='intervalo_1')
        return intervalo  # type: ignore

    def __validacao_campos(self) -> bool:
        if self.acao:
            return True
        else:
            self.st.sidebar.warning(
                'Campo "Nome da ação" não pode estar vazio')
            return False


if __name__ == '__main__':
    Programa()
