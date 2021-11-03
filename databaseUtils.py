import sqlite3
from sqlite3 import Error
from CryptoClass import CryptoItem

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


def check_db_tables_for_currency(current_columns: list, cryptoItems: list[CryptoItem], dbconn: str):
    crypto_list = [x[1].upper() for x in current_columns]
    for item in cryptoItems.crypto_list:
        if item.unitcount > 0 and item.symbol not in crypto_list:
            print("Adding column {}".format(item.symbol.lower()))
            result = execute_read_query(dbconn, "ALTER TABLE crypto ADD COLUMN " + item.symbol.lower() + " INTEGER")


def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")

def execute_write(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
    except Error as e:
        print(f"The error '{e}' occurred")