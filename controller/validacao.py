from datetime import datetime, timedelta


class Validacao:
    def __init__(self) -> None:
        pass

    @staticmethod
    def min_max_data_inicial(intervalo: str) -> list:
        match intervalo:
            case '1m':
                return [datetime.today(), datetime.today() - timedelta(days=30)]
            case '2m' | '5m' | '15m' | '30m' | '90m':
                return [datetime.today(), datetime.today() - timedelta(days=60)]
            case '1h':
                return [datetime.today(), datetime.today() - timedelta(days=730)]
            case _:
                return [datetime.today(), datetime.strptime('2000-01-01', '%Y-%m-%d')]
