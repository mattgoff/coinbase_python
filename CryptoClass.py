import requests


class CryptoItemList:
    exchange_rates = {}
    crypto_list = []

    @staticmethod    
    def addCrypto(name, symbol, unitcount):
        CryptoItemList.crypto_list.append(CryptoItem(name, symbol, unitcount))

    @classmethod
    def get_exchange_rates(cls) -> list:
        response = requests.get("https://api.coinbase.com/v2/exchange-rates")
        cls.exchange_rates = response.json()["data"]["rates"]


class CryptoItem:
    def __init__(self, name, symbol, unitcount):
        self.name = name
        self.symbol = symbol.upper()
        self.unitcount = unitcount

    def value(self):
        return self.unitcount / float(CryptoItemList.exchange_rates[self.symbol])
