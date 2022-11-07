"""main.py"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go

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
                with self.st.expander('Gráfico em candlestick'):
                    self.grafico_candlestick(dados_carregado)
                col1, col2, col3 = self.st.columns(3)
                with col1:
                    self.st.write('Preço atual')
                    self.st.write(dados_carregado['Close'].iloc[-1])
                with col2:
                    self.st.write('Mediana')
                    self.st.write(dados_carregado['Close'].median())
                with col3:
                    self.st.write('Log retorno')
                    self.st.write(np.log(dados_carregado['Close'].iloc[-1]))
                preparacao = Preparacao(dados_carregado)
                with self.st.expander('Gráfico da decompose_serie'):
                    self.grafico_decompose(
                        preparacao.decompose_serie.seasonal)
                with self.st.expander('Gráfico QQ Normal Plot'):
                    self.grafico_qqplot(preparacao.serie)

                self.st.header('Teste de shapiro')
                col3, col4 = self.st.columns(2)
                with col3:
                    self.st.write(f'Estatíca do teste: ',
                                  preparacao.teste_shapiro[0])
                with col4:
                    self.st.write(f'p-valor: ', preparacao.teste_shapiro[1])
            else:
                st.warning('Dados não encontrados!')

    def grafico_candlestick(self, dataframe: pd.DataFrame) -> None:
        range_lines = self.st.checkbox('Ranges Lider')
        fig = go.Figure(data=[go.Candlestick(x=dataframe.index, open=dataframe['Open'],
                        high=dataframe['High'], low=dataframe['Low'], close=dataframe['Close'])])
        fig.update_layout(xaxis_rangeslider_visible=False)
        self.st.plotly_chart(fig, use_container_width=range_lines)

    def grafico_decompose(self, serie: pd.Series) -> None:
        fig = go.Figure(
            data=[go.Scatter(x=serie.index, y=serie)])
        self.st.plotly_chart(fig, use_container_width=True)

    def grafico_qqplot(self, serie: pd.Series):
        fig = go.Figure(
            data=[go.Line(x=serie.index, y=serie)])
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
