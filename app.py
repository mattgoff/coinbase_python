import sqlite3

import requests
import hmac
import hashlib
import time
from datetime import datetime
from colorama import init

from databaseUtils import create_connection, check_db, execute_read_query, execute_write
from secrets import APIKey, APISecret
from CryptoClass import CryptoItemList
from displayData import output_data_colored, output_data_symbol

CBABaseURL = "https://api.coinbase.com/"


def generate_signature(
        timestamp: int, method: str, requestPath: str, body: str, appSecret: str
) -> str:
    message = f"{timestamp}{method}{requestPath}{body}"
    signature = hmac.new(
        appSecret.encode(), message.encode(), hashlib.sha256
    ).hexdigest()
    return signature


def get_section(api_key: str, signature: str, timeStamp: int, next_uri: str) -> object:
    headers = {
        "Content-Type": "application/json",
        "CB-ACCESS-KEY": api_key,
        "CB-ACCESS-SIGN": signature,
        "CB-ACCESS-TIMESTAMP": f"{timeStamp}",
    }
    response = requests.get(CBABaseURL + next_uri, headers=headers)
    next_uri = response.json()["pagination"]["next_uri"]
    return response.json()["data"], next_uri


def get_crypto_data() -> list:
    json_results = []
    next_uri = "/v2/accounts"

    while next_uri:
        time_stamp = int(time.time())
        signature = generate_signature(time_stamp, "GET", next_uri, "", APISecret)
        data, next_uri = get_section(APIKey, signature, time_stamp, next_uri)
        json_results += data

    return json_results


def add_to_crypto_list(data: list, crypto_item_list: [CryptoItemList]):
    for item in data:
        name = item["name"]
        amount = float(item["balance"]["amount"])
        currency = item["balance"]["currency"]
        crypto_item_list.add_crypto(name, currency, amount)


def add_to_crypto_db(crypto_item_list: [CryptoItemList], db_conn: sqlite3.Connection):
    dt = datetime.now().isoformat()
    col_values = "datetime,"
    val_values = '"{}",'.format(dt)
    val_total = 0

    for item in crypto_item_list.crypto_list:
        if item.unit_count > 0:
            col_values += "{},".format(item.symbol.lower())
            val_values += "{},".format(item.value())
            val_total += item.value()

    col_values += "total"
    val_values += "{}".format(val_total)

    sql_string = "INSERT into crypto({}) values({})".format(col_values, val_values)
    execute_write(db_conn, sql_string)


def get_rest_data():
    data = requests.get("http://172.16.12.11:5000/api/v1/aqi")
    return data.json()


def main():
    # get and populate exchange rates for all cryptos
    CryptoItemList.get_exchange_rates()

    # get crypto values in our portfolio
    json_results = get_crypto_data()

    # write crypto to object
    add_to_crypto_list(json_results, CryptoItemList)

    # connect to db and check that we have columns for each crypto that we own
    # db_conn = create_connection("./coinbase.sqlite")
    db_conn = create_connection("/home/pi/coinbase_python/coinbase.sqlite")
    current_columns = execute_read_query(db_conn, "PRAGMA table_info(crypto)")
    check_db(current_columns, CryptoItemList, db_conn)

    # write crypto to db
    add_to_crypto_db(CryptoItemList, db_conn)

    # get json office data
    office_json = get_rest_data()

    # output last pull to the screen with delta
    output_data_colored(db_conn, office_json)
    # output_data_symbol(db_conn)

    db_conn.close()
    CryptoItemList.crypto_list = []


if __name__ == "__main__":
    init(autoreset=True)

    while True:
        main()
        for i in range(60):
            print(".", end='')
            time.sleep(5)
