import requests
import hmac
import hashlib
import time
from datetime import datetime

from databaseUtils import create_connection, check_db, execute_read_query, execute_write
from secrets import APIKey, APISecret
from CryptoClass import CryptoItemList
from displayData import output_data_colored

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


def get_crypto_data() -> list:
    jsonResults = []
    NextURI = "/v2/accounts"

    while NextURI != None:
        timeStamp = int(time.time())
        signature = generate_signature(timeStamp, "GET", NextURI, "", APISecret)
        data, NextURI = get_section(APIKey, signature, timeStamp, NextURI)
        jsonResults += data

    return jsonResults


def add_to_crypto_list(data: list, CryptoItemList: [CryptoItemList]):
    for item in data:
        name = item["name"]
        amount = float(item["balance"]["amount"])
        currency = item["balance"]["currency"]
        CryptoItemList.addCrypto(name, currency, amount)


def add_to_crypto_db(CryptoItemList: [CryptoItemList], dbconn: str):
    dt = datetime.now().isoformat()
    col_values = "datetime,"
    val_values = '"{}",'.format(dt)
    val_total = 0

    for item in CryptoItemList.crypto_list:
        if item.unitcount > 0:
            col_values += "{},".format(item.symbol.lower())
            val_values += "{},".format(item.value())
            val_total += item.value()

    col_values += "total"
    val_values += "{}".format(val_total)

    sql_string = "INSERT into crypto({}) values({})".format(col_values, val_values)
    execute_write(dbconn, sql_string)


def main():
    # get and populate exchange rates for all cryptos
    CryptoItemList.get_exchange_rates()

    # get crypto values in our portfolio
    JSonResults = get_crypto_data()

    # write crypto to object
    add_to_crypto_list(JSonResults, CryptoItemList)

    # connect to db and check that we have columns for each crypto that we own
    dbconn = create_connection("./coinbase.sqlite")
    current_columns = execute_read_query(dbconn, "PRAGMA table_info(crypto)")
    check_db(current_columns, CryptoItemList, dbconn)

    # write crypto to db
    add_to_crypto_db(CryptoItemList, dbconn)

    # output last pull to the screen with delta
    output_data_colored(dbconn)

    dbconn.close()
    CryptoItemList.crypto_list = []


if __name__ == "__main__":
    while True:
        main()
        time.sleep(600)
