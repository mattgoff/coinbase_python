import os

from colorama.ansi import Fore
from CryptoClass import CryptoItem
from colorama import init, Fore

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

def output_data_colored(cryptoItems: list[CryptoItem]) -> None:
    pass