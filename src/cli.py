import pyfiglet
import json
import threading
from time import sleep as wait
import curses
from typing import Optional
from rich.console import Console
import os
from ban_check import check
from scratchattach import login as __login
from scratchattach.utils.exceptions import LoginFailure
from tqdm import tqdm
import csv
from pathlib import Path
import queue
print("INITIALIZING BOT SCRIPTS")
from manual_bot import manual_bot
from control_bots import connect, post
from bot import bot
print("INITIALIZED")
# The banner for the CLI
banner: str = pyfiglet.figlet_format("PyFleet Scratch", font="slant")
# Stores threads to detect when all threads have stopped
threads = []
stop_event = threading.Event()
console = Console()
# Create queue to hold results
q = queue.Queue()

print("INITIALIZED")


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(banner)


def worker(username, password):
    result = check(username, password)
    q.put(result)


clear()
wait(1)


def main():
    try:
        def control_bots():
            """
            Function that allows you to control the bots
            :return:
            """
            objects = []

            with open("config.json", 'r') as file:
                data = json.load(file)
                logins = data["BOTS"]
                project = data["TARGET"]

            for username, password in tqdm(logins, desc="INITIALIZING BOTS", unit=" BOTS"):
                objects.append(connect(username, password, project))

            print("BOTS HAVE SUCCESSFULLY STARTED")

            while True:
                message = input("POST (ENTER NOTHING TO END SESSION): ")
                if message != "":
                    for _object in objects:
                        post(_object, message)
                    print("COOLDOWN")
                    for _ in tqdm(range(30)):
                        wait(1)
                else:
                    clear()
                    return

        def check_bots():
            """
            Checks the bots for moderation that has affected them
            :return:
            """
            global threads

            _options = ["CHECK LOADED BOTS", "CANCEL"]
            _choice = curses.wrapper(lambda stdscr: choice(stdscr, _options, menu="CHECK BOTS:"))
            results = []
            if _choice == "CHECK LOADED BOTS":
                with open("config.json", 'r') as file:
                    _preferences = json.load(file)
                    logins = _preferences["BOTS"]

                for _login in logins:
                    thread = threading.Thread(target=worker, args=(_login[0], _login[1]))
                    thread.start()
                    threads.append(thread)

                for thread in threads:
                    thread.join()

                while not q.empty():
                    results.append(q.get())
                # Filters the logins
                cleaned = [x for x in results if x is not None]
                existing = [acc for acc in cleaned if acc in logins]
                # Deletes accounts that have been banned
                with open("config.json", 'w') as file:
                    _preferences["BOTS"] = existing
                    json.dump(_preferences, file, indent=2)

                print(f"YOU HAVE {len(existing)} BOTS")
                input("PRESS 'ENTER' TO CONTINUE\n")
                threads = []
            clear()

        def fire_bots():
            """
            Runs the loaded bots
            :return:
            """
            global threads

            _options = ["FIRE LOADED BOTS", "CANCEL"]
            _choice = curses.wrapper(lambda stdscr: choice(stdscr, _options, menu="FIRE BOTS:"))

            if _choice == "FIRE LOADED BOTS":
                console.print(
                    "THE BOTS WILL START IN [bold white]5[/bold white] SECONDS\n[bold green]>TO STOP BOTS PRESS ENTER<[/bold green]"
                )
                wait(5)
                with open("config.json", 'r') as file:
                    _preferences = json.load(file)
                    logins = _preferences["BOTS"]
                    bot_type = _preferences["BOT TYPE"]
                    outputs = _preferences["OUTPUTS"]

                if all(not x for x in outputs) and bot_type == "MANUAL":
                    print("NO ITEMS IN OUTPUTS")
                    wait(2)
                    clear()
                    return

                for _login in logins:
                    thread = threading.Thread(
                        target=bot if bot_type == "AI" else manual_bot,
                        args=(_login[0], _login[1], stop_event)
                    )
                    thread.start()
                    threads.append(thread)

                input()
                console.print("[bold white]STOPPING BOTS...[/bold white]")
                stop_event.set()

                for thread in threads:
                    thread.join()

                console.print("[bold green]>ALL BOTS HAVE STOPPED<[/bold green]")
                threads = []
                stop_event.clear()
                wait(1)
                clear()
            else:
                return

        def load_bots():
            """
            Loads bot credentials into preferences.json
            :return:
            """
            _options = ["ADD BOTS", "CANCEL"]
            _choice = curses.wrapper(lambda stdscr: choice(stdscr, _options, menu="LOAD BOTS:"))
            if _choice == "ADD BOTS":
                _options = ["ENTER THROUGH INPUTS", "UPLOAD CSV"]
                _choice = curses.wrapper(lambda stdscr: choice(stdscr, _options, menu="LOAD BOTS:"))

                if _choice == "UPLOAD CSV":
                    try:
                        _path = input("ENTER A FILE PATH: ")
                        path = Path(_path).expanduser()

                        with path.open(newline='') as file:
                            reader = csv.reader(file)
                            print("CHECKING ACCOUNTS")

                            for row in reader:
                                username, password = row[0], row[1]
                                try:
                                    __login(username, password)

                                    with open("config.json", 'r') as _file:
                                        data = json.load(_file)

                                    existing_usernames = {_bot[0] for _bot in data.get("BOTS", [])}
                                    if username not in existing_usernames:
                                        data["BOTS"].append(row)

                                        with open("config.json", 'w') as _file:
                                            json.dump(data, _file, indent=2)

                                    else:
                                        print(f"SKIPPING DUPLICATE")

                                except LoginFailure:
                                    print(f"FAILED TO LOGIN TO {username}")
                                    wait(1)

                    except FileNotFoundError:
                        print("FILE DOES NOT EXIST")
                else:
                    username = input("USERNAME: ")
                    password = input("PASSWORD: ")
                    credentials = [username, password]
                    print("CHECKING ACCOUNT")
                    try:
                        __login(username, password)
                        with open("config.json", 'r') as _file:
                            data = json.load(_file)
                        with open("config.json", 'w') as _file:
                            data["BOTS"].append(credentials)
                            json.dump(data, _file, indent=2)
                    except LoginFailure:
                        print("FAILED TO LOGIN")
                wait(1)
                clear()
            else:
                return

        def preferences():
            """
            Changes the contents of preferences.json
            :return:
            """
            _options = ["DEBUG", "LOGS", "TARGET", "PROMPT", "BOT TYPE", "OUTPUTS", "RATELIMIT", "CANCEL"]
            _choice = curses.wrapper(lambda stdscr: choice(stdscr, _options, menu="PREFERENCES:"))

            with open("config.json", 'r') as file:
                _preferences = json.load(file)

            match _choice:
                case "DEBUG":
                    _options = ["True", "False", "CANCEL"]
                    info = f"\nCURRENT VALUE: {_preferences["DEBUG"]}"
                    _choice = curses.wrapper(lambda stdscr: choice(stdscr, _options, menu="SELECT VALUE:", info=info))
                    if _choice == "CANCEL":
                        return
                    _preferences["DEBUG"] = True if _choice == "True" else False

                case "LOGS":
                    _options = ["True", "False", "CANCEL"]
                    info = f"\nCURRENT VALUE: {_preferences["LOGS"]}"
                    _choice = curses.wrapper(lambda stdscr: choice(stdscr, _options, menu="SELECT VALUE:", info=info))
                    if _choice == "CANCEL":
                        return
                    _preferences["LOGS"] = True if _choice == "True" else False

                case "TARGET":
                    try:
                        print(f"CURRENT VALUE: {_preferences["TARGET"]}")
                        _choice = int(input("ENTER A PROJECT ID (ENTER NOTHING TO CANCEL): "))
                    except ValueError:
                        print("NOT A VALID INTEGER")
                        return
                    if _choice != "":
                        _preferences["TARGET"] = _choice

                case "PROMPT":
                    print(f"CURRENT VALUE: {_preferences["PROMPT"]}")
                    _choice = input(
                        "ENTER THE AI's PROMPT (USE %u FOR USERNAME AND %c FOR COMMENT, ENTER NOTHING TO CANCEL): ")
                    if _choice != "":
                        _preferences["PROMPT"] = _choice

                case "BOT TYPE":
                    _options = ["AI", "MANUAL", "CANCEL"]
                    info = f"\nCURRENT VALUE: {_preferences["BOT TYPE"]}"
                    _choice = curses.wrapper(lambda stdscr: choice(stdscr, _options, menu="SELECT VALUE:", info=info))
                    if _choice == "CANCEL":
                        return
                    _preferences["BOT TYPE"] = _choice

                case "OUTPUTS":
                    print(f"CURRENT VALUE: {_preferences["OUTPUTS"]}")
                    _choice = input("ENTER AN OUTPUT FOR THE MANUAL BOT (ENTER NOTHING TO CANCEL): ")
                    if _choice != "":
                        _preferences["OUTPUTS"].append(_choice)

                case "RATELIMIT":
                    print(f"CURRENT VALUE: {_preferences["RATELIMIT"]}")
                    _choice = input("ENTER AMOUNT OF SECONDS FOR BOT TO PAUSE (ENTER NOTHING TO CANCEL): ")
                    try:
                        if _choice != "":
                            _preferences["RATELIMIT"] = int(_choice)
                    except ValueError:
                        print("INVALID INTEGER")

                case "CANCEL":
                    return

            with open("config.json", 'w') as file:
                json.dump(_preferences, file, indent=2)
            clear()

        def choice(stdscr, choices, _banner: Optional[str] = banner, menu: Optional[str] = "MENU:",
                   info: Optional[str] = ""):
            """
            This function creates a terminal menu for this CLI
            :param stdscr:
            :param choices:
            :param _banner:
            :param menu:
            :param info:
            :return:
            """
            curses.curs_set(0)
            stdscr.keypad(True)
            curses.start_color()
            current = 0
            row = 0

            banner_lines = _banner.splitlines()
            banner_height = len(banner_lines)

            curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)

            while True:
                stdscr.clear()
                height, width = stdscr.getmaxyx()

                for i, line in enumerate(banner_lines):
                    if i < height:
                        stdscr.addstr(i, 0, line[:width - 1])

                menu_row = banner_height + 1
                if menu_row < height:
                    stdscr.addstr(menu_row, 0, menu[:width - 1])

                for i, _choice in enumerate(choices):
                    row = menu_row + 1 + i
                    if row >= height:
                        break
                    text = _choice[:width - 1]
                    if i == current:
                        stdscr.addstr(row, 0, "> " + text, curses.color_pair(1) | curses.A_BOLD)
                    else:
                        stdscr.addstr(row, 2, text)

                stdscr.addstr(row + 1, 0, info)
                stdscr.refresh()

                key = stdscr.getch()
                if key == curses.KEY_UP and current > 0:
                    current -= 1
                elif key == curses.KEY_DOWN and current < len(choices) - 1:
                    current += 1
                elif key in (curses.KEY_ENTER, 10, 13):
                    return choices[current]

        def cli():
            """
            This just gets the selected option then runs the corresponding function
            :return:
            """
            with open("config.json", 'r') as file:
                data = json.load(file)
            if data["API KEY"] == "":
                _options = ["ENTER HUGGINGFACE API KEY", "SKIP", "EXIT"]
                _choice = curses.wrapper(lambda stdscr: choice(stdscr, _options, menu="SETUP:"))
                match _choice:
                    case "ENTER HUGGINGFACE API KEY":
                        key = input("API KEY (ENTER NOTHING TO CANCEL): ")
                        if key != "":
                            data["API KEY"] = key
                            with open("config.json", 'w') as file:
                                json.dump(data, file, indent=2)
                    case "SKIP":
                        pass
                    case "EXIT":
                        exit()

            _options = ["LOAD BOTS", "FIRE BOTS", "PREFERENCES", "CHECK BOTS", "CONTROL BOTS", "EXIT"]
            while True:
                _choice = curses.wrapper(lambda stdscr: choice(stdscr, _options))
                match _choice:
                    case "LOAD BOTS":
                        load_bots()
                    case "FIRE BOTS":
                        fire_bots()
                    case "PREFERENCES":
                        preferences()
                    case "CHECK BOTS":
                        check_bots()
                    case "CONTROL BOTS":
                        control_bots()
                    case "EXIT":
                        exit()

        cli()
    except KeyboardInterrupt:
        return
