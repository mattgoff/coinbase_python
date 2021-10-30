import requests

class CryptoItemList:
    exchange_rates = {}
    cyrpto_list = []

    def addCrypto(self, name, symbol, unitcount):
        CryptoItemList.cyrpto_list.append(CryptoItem(name, symbol, unitcount))
    
    @classmethod
    def get_exchange_rates(cls) -> list:
        response = requests.get('https://api.coinbase.com/v2/exchange-rates')
        cls.exchange_rates = response.json()['data']['rates']

class CryptoItem:
    def __init__(self, name, symbol, unitcount):
        self.name = name
        self.symbol =  symbol.upper()
        self.unitcount = float(unitcount)

    def value(self):
        return self.unitcount / float(CryptoItemList.exchange_rates[self.symbol])
