import os

from colorama.ansi import Fore
from CryptoClass import CryptoItem, CryptoItemList
from colorama import init, Fore
from databaseUtils import execute_read_query

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

def output_data_colored(dbconn: str) -> None:
    # clear_screen()
    init(autoreset=True)
    sql_string = "SELECT * FROM crypto ORDER by id DESC LIMIT 2"
    results = execute_read_query(dbconn, sql_string)
    if len(results) == 2:
        col_names = execute_read_query(dbconn, "PRAGMA table_info(crypto)")
        col_names = [x[1] for x in col_names]
        for symbol,c_cur, c_prev in zip(col_names, results[0], results[1]):
            if symbol != "id" and symbol != "datetime":
                full_name = ""
                for item in CryptoItemList.crypto_list:
                    if item.symbol.lower() == symbol.lower():
                        full_name = item.name
                if c_cur > c_prev:
                    print(Fore.GREEN + "{}\t{}\t{}".format(full_name,symbol, round(c_cur, 2)))
                elif c_prev < c_prev:
                    print(Fore.RED + "{}\t{}\t{}".format(full_name,symbol, round(c_cur, 2)))
                else:
                    print(Fore.BLUE + "{}\t{}\t{}".format(full_name,symbol, round(c_cur, 2)))
    else:
        print(Fore.YELLOW + "Try running it again")

