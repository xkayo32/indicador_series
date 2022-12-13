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
        previsao = ativo_controller.base_previsao()
        tendencia = ativo_controller.tendencia()
        context = {'grafico_candle': ativo_controller.grafico_candle(), 'grafico_tendencia': ativo_controller.grafico_tendencia(), 'dataframe': dataframe,
                   'infor_ativo': ativo_controller.infor_ativo, 'previsao': previsao, 'tendencia': tendencia, 'ultima_tendencia': previsao.loc[previsao['data'] == POST['data_final']]}
    else:
        context = {}

    return render(request, 'pages/previsao.html', context)
