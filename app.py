import requests
import hmac
import hashlib
import time
import os
from secrets import APIKey, APISecret
from CryptoClass import CryptoItem, CryptoItemList

CBABaseURL = "https://api.coinbase.com/"


def generate_signature(
    timestamp: str, method: str, requestPath: str, body: str, appSecret: str
) -> str:
    message = f"{timestamp}{method}{requestPath}{body}"
    signature = hmac.new(
        appSecret.encode(), message.encode(), hashlib.sha256
    ).hexdigest()
    return signature


def get_section(APIKey: str, signature: str, timeStamp: str, nextURI: str) -> object:
    headers = {
        "Content-Type": "application/json",
        "CB-ACCESS-KEY": APIKey,
        "CB-ACCESS-SIGN": signature,
        "CB-ACCESS-TIMESTAMP": f"{timeStamp}",
    }
    response = requests.get(CBABaseURL + nextURI, headers=headers)
    nextURI = response.json()["pagination"]["next_uri"]
    return (response.json()["data"], nextURI)


def clear_screen() -> None:
    clear = lambda: os.system("clear")
    clear()


def output_data(cryptoItems: list[CryptoItem]) -> None:
    totalValue = 0

    clear_screen()
    print(f"Name\t\tSymbol\tUnits\t\tValue")
    for item in cryptoItems:
        if item.unitcount > 0:
            totalValue += item.value()
            print(
                f"{item.name}\t{item.symbol}\t{item.unitcount}\t{round(item.value(), 2):.2f}"
            )

    print("-" * 36)
    print(f"Total Value: {round(totalValue, 2):.2f}")


def get_crypto_data() -> list:
    jsonResults = []
    NextURI = "/v2/accounts"

    while NextURI != None:
        timeStamp = int(time.time())
        signature = generate_signature(timeStamp, "GET", NextURI, "", APISecret)
        data, NextURI = get_section(APIKey, signature, timeStamp, NextURI)
        jsonResults += data

    return jsonResults


def add_to_crypto_list(data: dict, crypto: CryptoItemList):
    for item in data:
        name = item["name"]
        amount = float(item["balance"]["amount"])
        currency = item["balance"]["currency"]
        crypto.addCrypto(name, currency, amount)


if __name__ == "__main__":

    crypto = CryptoItemList()
    CryptoItemList.get_exchange_rates()
    JSonResults = get_crypto_data()
    add_to_crypto_list(JSonResults, crypto)
    output_data(CryptoItemList.cyrpto_list)
