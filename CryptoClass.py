import requests


class CryptoItemList:
    exchange_rates = {}
    crypto_list = []

    @staticmethod    
    def add_crypto(name, symbol, unit_count):
        CryptoItemList.crypto_list.append(CryptoItem(name, symbol, unit_count))

    @classmethod
    def get_exchange_rates(cls) -> None:
        response = requests.get("https://api.coinbase.com/v2/exchange-rates")
        cls.exchange_rates = response.json()["data"]["rates"]


class CryptoItem:
    def __init__(self, name, symbol, unit_count):
        self.name = name
        self.symbol = symbol.upper()
        self.unit_count = unit_count

    def value(self):
        return self.unit_count / float(CryptoItemList.exchange_rates[self.symbol])
