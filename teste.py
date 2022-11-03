import pandas as pd

te = pd.DataFrame()

te2 = pd.DataFrame(data=['casa', 'carro', 'moto'])
print(pd.concat([te, te2]))
