import pyfiglet
from bot import bot
import json
import threading
from time import sleep as wait
from pathlib import Path

banner: str = pyfiglet.figlet_format("PyFleet Scratch", font="slant")
options: str = """
1. LOAD BOTS
2. FIRE BOTS
3. PREFERENCES
4. EXIT"""
threads = []
stop_event = threading.Event()

print(banner)
wait(1)


def fire_bots():
    print("TO STOP BOTS PRESS ENTER")
    wait(5)
    with open("logins.txt", 'r') as file:
        logins = file.read().split("\n")

    for _login in logins:
        login = _login.split(" ")
        thread = threading.Thread(target=bot, args=(login[0], login[1], stop_event))
        thread.start()
        threads.append(thread)

    input()
    print("STOPPING BOTS...")
    stop_event.set()

    for thread in threads:
        thread.join()

    print("ALL BOTS HAVE STOPPED")


def load_bots():
    path = Path(input("\nPLEASE ENTER A FILE PATH: "))

    if not path.name == '':
        extension = path.suffix
        if extension in ("txt", "text"):
            with open(path, 'r') as file:
                contents = file.read()

            with open("logins.txt", 'w') as file:
                file.write(contents)
            print(path)
        else:
            print("THE FILE THAT WAS PROVIDED IS NOT A TEXT FILE")
    else:
        print("NO FILE CHOSEN")


def preferences():
    value = ""  # Define

    with open("preferences.json", 'r') as file:
        _preferences = json.load(file)

    print("\nCHANGE ANY OF THESE VALUES:\n1. DEBUG: bool\n2. LOGS: bool\n3. prompt: str\n4. target: int")
    option = input("OPTION: ")

    match option:
        case "1":
            value = "DEBUG:" + input("NEW VALUE: ")
        case "2":
            value = "LOGS:" + input("NEW VALUE: ")
        case "3":
            value = "prompt:" + input("NEW VALUE: ")
        case "4":
            value = "target:" + input("NEW VALUE: ")
        case _:
            value = "INVALID"

    if not value == "INVALID":
        _set = value.split(":")

        if _set[0] == "DEBUG":
            if _set[1].lower() == "true":
                _preferences["DEBUG"] = True
            elif _set[1].lower() == "false":
                _preferences["DEBUG"] = False
            else:
                print("VALUE FOR \"DEBUG\" IS NOT A VALID BOOLEAN")
        elif _set[0] == "LOGS":
            if _set[1].lower() == "true":
                _preferences["LOGS"] = True
            elif _set[1].lower() == "false":
                _preferences["LOGS"] = False
            else:
                print("VALUE FOR \"DEBUG\" IS NOT A VALID BOOLEAN")
        elif _set[0] == "prompt":
            _preferences["prompt"] = _set[1]
        elif _set[0] == "target":
            try:
                _preferences["target"] = int(_set[1])
            except ValueError:
                print("VALUE FOR \"target\" IS NOT A VALID INTEGER")
        else:
            print("INVALID")

    with open("preferences.json", 'w') as file:
        json.dump(_preferences, file, indent=4)


def cli():
    while True:
        print(options)
        option = input("OPTION: ")

        match option:
            case "1":
                load_bots()
            case "2":
                fire_bots()
            case "3":
                preferences()
            case "4":
                exit()
            case _:
                print("INVALID OPTION")


if __name__ == "__main__":
    cli()
