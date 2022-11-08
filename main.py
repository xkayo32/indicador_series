"""main.py"""

import numpy as np
import pandas as pd
import plotly.express as px
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
        tab1, tab2, tab3 = self.st.tabs(
            ['Análise', 'Normalização', 'Previsão'])
        if self.__validacao_campos():
            self.acao_controller = AtivoController(
                self.acao, self.data_inicial, self.data_final, self.intervalo)
            dados_carregado = self.acao_controller.download_ativos()
            if dados_carregado.size:  # type: ignore
                with tab1:
                    preparacao = Preparacao(dados_carregado)
                    with self.st.expander('Gráfico em candlestick'):
                        self.grafico_candlestick(dados_carregado)
                    with self.st.expander('Gráfico histograma'):
                        self.grafico_histograma(preparacao.serie)
                    with self.st.expander('Gráfico de tendencia'):
                        self.grafico_decomposicao(
                            preparacao.decomposicao.trend, 'Gráfico de tendencia')
                    with self.st.expander('Gráfico sazonal'):
                        self.grafico_decomposicao(
                            preparacao.decomposicao.seasonal, 'Gráfico sazonal')
                    with self.st.expander('Gráfico aleatoria'):
                        self.grafico_decomposicao(
                            preparacao.decomposicao.resid, 'Gráfico aleatoria')
                    col1, col2, col3, col4, col5, col6 = self.st.columns(6)
                    with col1:
                        self.st.write('Preço atual')
                        self.st.write(dados_carregado['Close'].iloc[-1])
                    with col2:
                        self.st.write('Mediana do período')
                        self.st.write(dados_carregado['Close'].median())
                    with col3:
                        self.st.write('Taxa retorno do período')
                        self.st.write(round(np.log(
                            dados_carregado['Close'].iloc[0] / dados_carregado['Close'].iloc[-1]) * 100, 2))
                    with col4:
                        self.st.write('Taxa de retorno intervalo')
                        self.st.write(round(np.log(
                            dados_carregado['Close'].iloc[-1] / dados_carregado['Close'].iloc[-2]) * 100, 2))
                    with col5:
                        self.st.write('Desvio padrão do período')
                        self.st.write(self.__retorno_logaritimo_periodo(
                            dados_carregado).std())
                    with col6:
                        self.st.write('Coef de variação do período')
                        self.st.write(stats.variation(
                            self.__retorno_logaritimo_periodo(dados_carregado)))
                    if dados_carregado.size < 30:
                        self.st.header('Teste de shapiro')
                        col10, col11 = self.st.columns(2)
                        w_c10, p_c10 = preparacao.teste_shapiro(
                            preparacao.serie)[0]
                        with col10:
                            self.st.write(f'Estatíca do teste: ', w_c10
                                          )
                        with col11:
                            self.st.write(
                                f'p-valor: ', p_c10)

                        if p_c10 > 0.05:
                            self.st.success('É uma distribuição normal')
                            normalizar = False
                        else:
                            self.st.error('Não é uma distribuição normal')
                            normalizar = True
                    else:
                        self.st.header('Teste de D’Agostino and Pearson’s')
                        col20, col21 = self.st.columns(2)
                        w_c20, p_c20 = preparacao.teste_person(
                            preparacao.dataframe)
                        with col20:
                            self.st.write('Estatíca do teste: ', w_c20[0])
                        with col21:
                            self.st.write('p-valor: ', p_c20[0])
                        if p_c20 > 0.05:
                            self.st.success('É uma distribuição normal')
                            normalizar = False
                        else:
                            self.st.error('Não é uma distribuição normal')
                            normalizar = True
                    with tab2:
                        if normalizar:
                            with self.st.expander('Gráfico histograma'):
                                self.grafico_histograma(
                                    preparacao.normalizacao_log)
                            if preparacao.normalizacao_log.size < 30:
                                col30, col31 = self.st.columns(2)
                                w_c30, p_c30 = preparacao.teste_shapiro(
                                    preparacao.normalizacao_log)
                                with col30:
                                    self.st.write('Estatíca do teste: ', w_c30)
                                with col31:
                                    self.st.write('p-valor: ', p_c30)
                            else:
                                col40, col41 = self.st.columns(2)
                                w_c40, p_c40 = preparacao.teste_person(
                                    preparacao.preparando_dataframe)
                                with col40:
                                    self.st.write(
                                        'Estatíca do teste: ', w_c40[0])
                                with col41:
                                    self.st.write('p-valor: ', p_c40[0])
                        else:
                            self.st.success(
                                'Oba! Os dados já estão normalizados')
                    with tab3:
                        self.st.success('Aguardando')
            else:
                st.warning('Dados não encontrados!')

    def grafico_candlestick(self, dataframe: pd.DataFrame) -> None:
        range_lines = self.st.checkbox('Ranges Lider')
        fig = go.Figure(data=[go.Candlestick(x=dataframe.index, open=dataframe['Open'],
                                             high=dataframe['High'], low=dataframe['Low'], close=dataframe['Close'])])
        fig.update_layout(xaxis_rangeslider_visible=range_lines)
        self.st.plotly_chart(fig, use_container_width=True)

    def grafico_histograma(self, serie) -> None:
        fig = go.Figure(
            data=[go.Histogram(x=serie)])
        self.st.plotly_chart(fig, use_container_width=True)

    def grafico_decomposicao(self, serie, titulo: str) -> None:
        fig = px.line(title=titulo).add_scatter(y=serie, x=serie.index)
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

    def __retorno_logaritimo_periodo(self, dados_carregado: pd.DataFrame):
        taxa_log = np.log(
            dados_carregado['Close'] / dados_carregado['Close'].shift(1)) * 100
        taxa_log = taxa_log[~np. isnan(taxa_log)]
        return taxa_log


if __name__ == '__main__':
    Programa()
