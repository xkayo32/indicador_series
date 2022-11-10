import plotly.express as px
import plotly.graph_objects as go
from django.shortcuts import render

from controller.controller import AtivoController

# Create your views here.

def home_page(request):
    return render(request,'pages/home.html')

def previsao_page(request):
    if request.method == 'POST':
        POST = request.POST
        ativo_controller = AtivoController(POST['acao'],POST['data_inicial'],POST['data_final'])
        dataframe = ativo_controller.base_dados
        fig2 = go.Figure(data=[go.Candlestick(x=dataframe.index, open=dataframe['Open'],
                                             high=dataframe['High'], low=dataframe['Low'], close=dataframe['Close'])])
        chart2 = fig2.to_html()
    context = {'fig2': chart2}
    return render(request,'pages/previsao.html',context)    