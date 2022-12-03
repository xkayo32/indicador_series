import random
import re
import string
from dataclasses import dataclass

import numpy as np
import pandas as pd
import spacy
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix)
from sklearn.model_selection import train_test_split
from spacy.lang.en import stop_words
from spacy.training import Example


@dataclass
class Base:
    base_treinamento:pd.DataFrame
    base_teste:pd.DataFrame


class PipelinePLN(Base):
    def __init__(self) -> None:
        self.pln = spacy.load('en_core_web_sm')

    def __pre_processamento_texto(self,texto:str) -> list:
        texto = texto.lower()
        texto = re.sub(r"@[a-zA-Z0-9$-_@&./+]+",'',texto)
        texto = re.sub(r"https?://[a-zA-Z0-9./]+",'',texto)
        texto = re.sub('\d+', '', texto)
        texto = self.pln(texto)
        texto = self.__lematizacao(texto)
        texto = self.__remover_stopwords(texto)
        return texto

    def __lematizacao(self,texto:list) -> list:
        return [palavra.lemma_ for palavra in texto]
    
    def __remover_stopwords(self,texto:list) -> list:
        return ' '.join([str(palavra) for palavra in texto if palavra not in stop_words.STOP_WORDS and palavra not in string.punctuation and not palavra.isdigit()])
    
    @property
    def limpeza(self) -> pd.DataFrame:
        dataframe = pd.read_csv(f'controller/data/stock_data.csv',header=0,on_bad_lines='skip')
        dataframe['Text'] = dataframe['Text'].apply(self.__pre_processamento_texto)
        dataframe['tamanho'] = dataframe['Text'].apply(len) # Numero de caracteres
        dataframe = dataframe.loc[dataframe['tamanho'] > 10]
        del dataframe['tamanho']
        dataframe.to_csv('controller/data/stock_clear_data.csv',index=False)
        return dataframe

    def __treinamento_pln(self) -> Base:
        dataframe = pd.read_csv(f'controller/data/stock_clear_data.csv')
        base_treinamento,base_teste = train_test_split(dataframe,test_size=0.3,stratify=dataframe['Sentiment'],random_state=1)
        base_treinamento = self.__tratamento_classe(base_treinamento)
        return Base(base_treinamento,base_teste)
    
    def avaliando_modelo(self):
        bases = self.__treinamento_pln()
        self.__criando_modelo(bases.base_treinamento)
        modelo_carregado  = spacy.load('controller/data/modelo')
        previsoes = [modelo_carregado(texto).cats for texto in bases.base_teste['Text']]
        previsoes_final = np.array([1 if previsao['POSITIVO'] > previsao['NEGATIVO'] else -1 for previsao in previsoes])
        return accuracy_score(bases.base_teste['Sentiment'], previsoes_final)
    
    def previsao_sentimento(self,texto:str):
        texto = self.__pre_processamento_texto(texto)
        
        return texto
    
    def __criando_modelo(self,base_treinamento_final):
        modelo = spacy.blank('en')
        categoria = modelo.create_pipe('textcat')
        categoria.add_label('POSITIVO')
        categoria.add_label('NEGATIVO')
        modelo.begin_training()
        for _ in range(5):
            random.shuffle(base_treinamento_final)
            for batch in spacy.util.minibatch(base_treinamento_final, 512):
                textos = [modelo.make_doc(texto) for texto, entities in batch]
                annotations = [{'cats': entities} for texto, entities in batch]
                example = Example.from_dict(textos,annotations)
                modelo.update([example])
        modelo.to_disk('controller/data/modelo')
            
    def __tratamento_classe(self,base_treinamento:pd.DataFrame)-> pd.DataFrame:
        return [[valor.Text, {'POSITIVO':True,'NEGATIVO':False} if valor.Sentiment == 1 else {'POSITIVO':False,'NEGATIVO':True}] for valor in base_treinamento.itertuples()]

        


if __name__ == '__main__':
    pipline = PipelinePLN()
    pipline.avaliando_modelo()
    base = pipline.previsao_sentimento("When AMZN monetize all electronics it makes with traffic to marketplace, AAP 3.5 GOOG will wake up and say why didn't we buy EBAY")
    print(base)