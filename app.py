import requests
import hmac
import hashlib
import time
import os
from datetime import datetime

from databaseUtils import create_connection, check_db_tables_for_currency, execute_read_query, execute_write
from secrets import APIKey, APISecret
from CryptoClass import CryptoItem, CryptoItemList
from displayData import output_data

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


def add_to_crypto_list(data: dict, CryptoItemList: CryptoItemList):
    for item in data:
        name = item["name"]
        amount = float(item["balance"]["amount"])
        currency = item["balance"]["currency"]
        CryptoItemList.addCrypto(name, currency, amount)


def add_to_crypto_db(CryptoItemList: CryptoItemList, dbconn: str):
    dt = datetime.now().isoformat()
    col_values = "datetime,"
    val_values = '"{}",'.format(dt)

    for item in CryptoItemList.crypto_list:
        if item.unitcount > 0:
            col_values += "{},".format(item.symbol.lower())
            val_values += "{},".format(item.value())

    col_values = col_values.rstrip(",")
    val_values = val_values.rstrip(",")

    sql_string = "INSERT into crypto({}) values({})".format(col_values, val_values)
    execute_write(dbconn, sql_string)


def main():  
    #get and populate exchange rates for all cryptos
    CryptoItemList.get_exchange_rates()

    #get crypto values in our portfolio
    JSonResults = get_crypto_data()

    #write crypto to object
    add_to_crypto_list(JSonResults, CryptoItemList)

    #connect to db and check that we have columns for each crypto that we own
    dbconn = create_connection("./coinbase.sqlite")
    current_columns = execute_read_query(dbconn, "PRAGMA table_info(crypto)")
    check_db_tables_for_currency(current_columns, CryptoItemList, dbconn)
    
    #write crypto to db
    add_to_crypto_db(CryptoItemList, dbconn)
    
    #output last pull to the screen with delta
    output_data(CryptoItemList.crypto_list)
    dbconn.close()

if __name__ == "__main__":
    main()

