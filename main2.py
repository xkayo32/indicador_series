teste = {'1': 'online', '2': 'online',
         '3': 'online', '4': 'offline', '5': 'offline'}


def busca_maiscula(teste):
    return len([y for _, y in teste.items() if y == 'online'])


print(busca_maiscula(teste))
