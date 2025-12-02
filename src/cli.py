print("INITIALIZING...")

import pyfiglet
from bot import bot
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
from manual_bot import manual_bot

banner: str = pyfiglet.figlet_format("PyFleet Scratch", font="slant")
threads = []
stop_event = threading.Event()
console = Console()
__preferences = {"PROMPT": "PROMPT", "DEBUG": True, "LOGS": True, "TARGET": 1, "BOT TYPE": "MANUAL", "OUTPUTS": [],
                 "BOTS": []}

if not os.path.exists("config.json"):
    with open('config.json', 'w') as f:
        json.dump(__preferences, f)


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(banner)


clear()

wait(1)


def main():
    try:
        def check_bots():
            """
            Checks the bots for moderation that has affected them
            :return:
            """
            _options = ["CHECK LOADED BOTS", "CANCEL"]
            _choice = curses.wrapper(lambda stdscr: choice(stdscr, _options, menu="CHECK BOTS:"))
            if _choice == "CHECK LOADED BOTS":
                with open("config.json", 'r') as file:
                    _preferences = json.load(file)
                    logins = _preferences["BOTS"]

                for _login in logins:
                    thread = threading.Thread(target=check, args=(_login[0], _login[1]))
                    thread.start()
                input("PRESS 'ENTER' TO CONTINUE\n")
            clear()

        def fire_bots():
            """
            Runs the loaded bots
            :return:
            """
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
                username = input("USERNAME: ")
                password = input("PASSWORD: ")

                try:
                    __login(username, password)
                except LoginFailure:
                    print("INVALID ACCOUNT CREDENTIALS")
                    wait(1)
                    clear()
                    return

                credentials = [username, password]
                with open("config.json", 'r+') as file:
                    _preferences = json.load(file)
                    _preferences["BOTS"].append(credentials)
                    file.seek(0)
                    json.dump(_preferences, file, indent=4)
                    file.truncate()
                clear()
            else:
                return

        def preferences():
            """
            Changes the contents of preferences.json
            :return:
            """
            _options = ["DEBUG", "LOGS", "TARGET", "PROMPT", "BOT TYPE", "OUTPUTS", "CANCEL"]
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
                        _choice = int(input("ENTER A PROJECT ID: "))
                    except ValueError:
                        print("NOT A VALID INTEGER")
                        return
                    _preferences["TARGET"] = _choice

                case "PROMPT":
                    print(f"CURRENT VALUE: {_preferences["PROMPT"]}")
                    _choice = input("ENTER THE AI's PROMPT (USE %u FOR USERNAME AND %c FOR COMMENT): ")
                    if not _choice == "CANCEL":
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
                    _choice = input("ENTER AN OUTPUT FOR THE MANUAL BOT (TYPE CANCEL TO CANCEL): ")
                    if not _choice == "CANCEL":
                        _preferences["OUTPUTS"].append(_choice)

                case "CANCEL":
                    return

            with open("config.json", 'w') as file:
                json.dump(_preferences, file, indent=4)
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
            _options = ["LOAD BOTS", "FIRE BOTS", "PREFERENCES", "CHECK BOTS", "EXIT"]
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
                    case "EXIT":
                        exit()

        cli()
    except KeyboardInterrupt:
        return


if __name__ == "__main__":
    main()
