import plotly.graph_objects as go
from django.shortcuts import redirect, render

from controller.controller import AtivoController

# Create your views here.


def home_page(request):
    return render(request, 'pages/home.html')


def previsao_page(request):
    if request.method == 'POST':
        POST = request.POST
        ativo_controller = AtivoController(
            POST['acao'], POST['data_inicial'], POST['data_final'])
        dataframe = ativo_controller.base_dados
        fig2 = go.Figure(data=[go.Candlestick(x=dataframe.index, open=dataframe['Open'],
                                              high=dataframe['High'], low=dataframe['Low'], close=dataframe['Close'])])
        previsao = ativo_controller.base_previsao
        tendencia = ativo_controller.tendencia(previsao)
        context = {'fig2': fig2, 'dataframe': dataframe,
                   'infor_ativo': ativo_controller.infor_ativo, 'previsao': previsao, 'tendencia': tendencia}
        return render(request, 'pages/previsao.html', context)
    return redirect('core:home_page')
