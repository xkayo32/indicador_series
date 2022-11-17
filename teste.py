from dataclasses import dataclass


@dataclass
class Teste:
    __nome:str
    __idade:int
    
teste1 = Teste('Kayo','25')

teste1.__nome = 'Andressa'

print(teste1)