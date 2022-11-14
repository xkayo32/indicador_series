"""main.py"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import scipy.stats as stats

from controller.controller import AtivoController
from controller.machine_stock import Preparacao
from controller.validacao import Validacao


class Programa(Validacao):
    def __init__(self) -> None:
        super().__init__()
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
        tab1, tab2 = self.st.tabs(
            ['Análise', 'Previsão'])
        if self.__validacao_campos():
            self.acao_controller = AtivoController(
                self.acao, self.data_inicial, self.data_final, self.intervalo)
            dados_carregado = self.acao_controller.download_ativos()
            if dados_carregado.shape[0] >= 14:  # type: ignore
                with tab1:
                    preparacao = Preparacao(dados_carregado)
                    with self.st.expander('Gráfico em candlestick'):
                        self.grafico_candlestick(dados_carregado)
                    with self.st.expander('Gráfico histograma'):
                        self.grafico_histograma(preparacao.serie)
                    with self.st.expander('Gráfico de tendencia'):
                        self.grafico_decomposicao(
                            preparacao.decomposicao(preparacao.serie).trend, 'Gráfico de tendencia')
                    with self.st.expander('Gráfico sazonal'):
                        self.grafico_decomposicao(
                            preparacao.decomposicao(preparacao.serie).seasonal, 'Gráfico sazonal')
                    with self.st.expander('Gráfico aleatoria'):
                        self.grafico_decomposicao(
                            preparacao.decomposicao(preparacao.serie).resid, 'Gráfico aleatoria')
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
                            dados_carregado['Close'].iloc[-1] / dados_carregado['Close'].iloc[0]) * 100, 2))
                    with col4:
                        self.st.write(
                            f'Taxa de retorno intervalo "{self.intervalo}"')
                        self.st.write(round(np.log(
                            dados_carregado['Close'].iloc[-1] / dados_carregado['Close'].iloc[-2]) * 100, 2))
                    with col5:
                        self.st.write('Desvio padrão do período')
                        self.st.write(self.__retorno_logaritimo_periodo(
                            dados_carregado).std())
                    col_msg, _ = self.st.columns(2)
                    col10, col11 = self.st.columns(2)
                    if dados_carregado.shape[0] < 30:
                        titulo_teste = 'Teste de shapiro'
                        w_c10, p_c10 = preparacao.teste_shapiro(
                            preparacao.serie)
                    else:
                        titulo_teste = "Teste D'Agostino Pearson"
                        w_c10, p_c10 = preparacao.teste_person(
                            preparacao.serie)
                    with col_msg:
                        self.st.header(titulo_teste)
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
                    with tab2:
                        algo_escolha = self.st.radio(
                            'Auto ARIMA', ('OFF', 'ON'), help='Com Auto ARIMA ativado pode demorar varios minutos para testar todos os parametros', horizontal=True)
                        if algo_escolha == 'OFF':
                            col_ar, col_i, col_ma = self.st.columns(3)
                            with col_ar:
                                ar_p = self.st.number_input(
                                    'AR', min_value=0, max_value=20, step=1, help='Modelo Auto Regressivo', value=1)
                            with col_i:
                                ar_d = self.st.number_input(
                                    'I', min_value=0, max_value=20, step=1, help='Número de diferenciações', value=1)
                            with col_ma:
                                ar_q = self.st.number_input(
                                    'MA', min_value=0, max_value=20, step=1, help='Média Móveis', value=1)
                            treinado = preparacao.arima_teste(
                                preparacao.serie, int(ar_p), int(ar_d), int(ar_q))
                            residuos_arima = treinado.resid
                            self.st.write('')
                            with self.st.expander('Informações do algoritimo'):
                                self.st.write(treinado.summary())
                            with self.st.expander('Grafico da previsão'):
                                pass
                            self.st.dataframe(
                                preparacao.previsao_arima(4))
                            col_res1, col_res2 = self.st.columns(2)
                            if len(residuos_arima) < 30:
                                w_res1, p_res2 = preparacao.teste_shapiro(
                                    residuos_arima)
                            else:
                                w_res1, p_res2 = preparacao.teste_person(
                                    residuos_arima)
                            with col_res1:
                                self.st.write('Estatíca do teste: ', w_res1)
                            with col_res2:
                                self.st.write('p-valor: ', p_res2)
                        else:
                            treinado_auto = preparacao.auto_arima_teste(
                                preparacao.serie)
                            self.st.write(
                                'Parametros do auto ARIMA: ', treinado_auto.order)
                            self.st.write(
                                preparacao.previsao_auto_arima(treinado_auto, preparacao.serie, 4))
                            self.st.dataframe(
                                preparacao.teste_treinamento_auto_arima())

            else:
                self.st.warning('Dados não encontrados!')

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

    def grafico_decomposicao(self, serie: pd.Series, titulo: str) -> None:
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
