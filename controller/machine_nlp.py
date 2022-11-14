import os
import re
import string

import pandas as pd
import spacy
from spacy.lang.en import stop_words


class TreinamentoNLP:
    def __init__(self) -> None:
        self.pln = spacy.load('en_core_web_sm')
        self.stop_words = stop_words.STOP_WORDS
    
    def pre_processamento_texto(self,texto):
        texto = texto.lower()
        texto = re.sub(r"@[a-zA-Z0-9$-_@&./+]+",'',texto)
        texto = re.sub(r"https?://[a-zA-Z0-9./]+",'',texto)
        texto = self.pln(texto)
        texto = self.__lematizacao(texto)
        texto = self.__remover_stopwords(texto)
        return texto

    def __lematizacao(self,texto):
        return [palavra.lemma_ for palavra in texto]
    
    def __remover_stopwords(self,texto:list):
        return ' '.join([str(palavra) for palavra in texto if palavra not in self.stop_words and palavra not in string.punctuation and not palavra.isdigit()])

    def limpeza(self):
        dataframe = pd.read_csv(f'/home/kayo/Documents/indicador_series/controller/data/base_tweets.csv',delimiter=';',header=0,on_bad_lines='skip')
        dataframe['text'] = dataframe['text'].apply(self.pre_processamento_texto)
        return dataframe

if __name__ == '__main__':
    t = TreinamentoNLP()
    print(t.limpeza())
