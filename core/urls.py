from django.urls import path

from core.views import *

app_name = 'core'

urlpatterns = [
    path('', home_page, name='home_page'),
    path('ativos/', ativos_page, name='ativos_page'),
    path('previsao/', previsao_page, name='previsao_page')
]
