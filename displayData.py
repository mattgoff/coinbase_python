import os
import sqlite3
from datetime import datetime
from CryptoClass import CryptoItem, CryptoItemList
from colorama import Fore
from databaseUtils import execute_read_query


def clear_screen() -> None:
    clear = lambda: os.system("clear")
    clear()


def output_data(cryptoItems: list[CryptoItem]) -> None:
    total_value = 0

    clear_screen()
    print(f"Name\t\tSymbol\tUnits\t\tValue")
    for item in cryptoItems:
        if item.unit_count > 0:
            total_value += item.value()
            print(
                f"{item.name}\t{item.symbol}\t{item.unit_count}\t{round(item.value(), 2):.2f}"
            )

    print("-" * 36)
    print(f"Total Value: {round(total_value, 2):.2f}")


def output_data_colored(db_conn: sqlite3.Connection) -> None:
    clear_screen()
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Time: ->  {}".format(current_time))

    sql_string = "SELECT * FROM crypto ORDER by id DESC LIMIT 2"
    results = execute_read_query(db_conn, sql_string)
    if len(results) == 2:
        col_names = execute_read_query(db_conn, "PRAGMA table_info(crypto)")
        col_names = [x[1] for x in col_names]
        for symbol, c_cur, c_prev in zip(col_names, results[0], results[1]):
            if symbol != "id" and symbol != "datetime":
                full_name = ""
                for item in CryptoItemList.crypto_list:
                    if item.symbol.lower() == symbol.lower():
                        full_name = item.name
                if c_cur > c_prev:
                    print(Fore.GREEN + "{}\t{}\t{}".format(full_name, symbol, round(c_cur, 2)))
                elif c_prev < c_prev:
                    print(Fore.RED + "{}\t{}\t{}".format(full_name, symbol, round(c_cur, 2)))
                else:
                    print(Fore.BLUE + "{}\t{}\t{}".format(full_name, symbol, round(c_cur, 2)))
    else:
        print(Fore.YELLOW + "Try running it again")


def output_data_symbol(db_conn: sqlite3.Connection) -> None:
    clear_screen()
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Time: ->  {}".format(current_time))

    sql_string = "SELECT * FROM crypto ORDER by id DESC LIMIT 2"
    results = execute_read_query(db_conn, sql_string)
    if len(results) == 2:
        col_names = execute_read_query(db_conn, "PRAGMA table_info(crypto)")
        col_names = [x[1] for x in col_names]
        for symbol, c_cur, c_prev in zip(col_names, results[0], results[1]):
            if symbol != "id" and symbol != "datetime":
                full_name = ""
                for item in CryptoItemList.crypto_list:
                    if item.symbol.lower() == symbol.lower():
                        full_name = item.name
                if c_cur > c_prev:
                    print("{}\t{}\t{}\t↑".format(full_name, symbol, round(c_cur, 2)))
                elif c_cur < c_prev:
                    print("{}\t{}\t{}\t↓".format(full_name, symbol, round(c_cur, 2)))
                else:
                    print("{}\t{}\t{}\t→".format(full_name, symbol, round(c_cur, 2)))
    else:
        print("←← Try running it again →→")
