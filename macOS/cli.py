print("INITIALIZING...")

import pyfiglet
from bot import bot
import json
import threading
from time import sleep as wait
from pathlib import Path
import curses
from typing import Optional
from rich.console import Console
import os

banner: str = pyfiglet.figlet_format("PyFleet Scratch", font="slant")
threads = []
stop_event = threading.Event()
console = Console()


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(banner)


clear()

wait(1)


def main():
    try:
        def fire_bots():
            _options = ["FIRE LOADED BOTS", "CANCEL"]
            _choice = curses.wrapper(lambda stdscr: choice(stdscr, _options, menu="FIRE BOTS:"))

            if _choice == "FIRE LOADED BOTS":
                console.print("THE BOTS WILL START IN [bold white]5[/bold white] SECONDS\n[bold green]>TO STOP BOTS PRESS ENTER<[/bold green]")
                wait(5)
                with open("logins.txt", 'r') as file:
                    logins = file.read().split("\n")

                for _login in logins:
                    login = _login.split(" ")
                    thread = threading.Thread(target=bot, args=(login[0], login[1], stop_event))
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
            _options = ["ENTER FILE PATH", "CANCEL"]
            _choice = curses.wrapper(lambda stdscr: choice(stdscr, _options, menu="LOAD BOTS:"))

            if _choice == "ENTER FILE PATH":
                path = Path(input("\nPLEASE ENTER A FILE PATH: ")).expanduser()

                if not path.name == '':
                    extension = path.suffix
                    if extension == ".txt":
                        with open(path, 'r') as file:
                            contents = file.read()

                        with open("logins.txt", 'w') as file:
                            file.write(contents)
                        clear()
                    else:
                        print("THE FILE THAT WAS PROVIDED IS NOT A TEXT FILE")
                        wait(1)
                        clear()
                else:
                    print("NO FILE CHOSEN")
                    wait(1)
                    clear()
            else:
                return

        def preferences():
            _options = ["DEBUG", "LOGS", "TARGET", "PROMPT", "CANCEL"]
            _choice = curses.wrapper(lambda stdscr: choice(stdscr, _options, menu="PREFERENCES:"))

            with open("preferences.json", 'r') as file:
                _preferences = json.load(file)

            match _choice:
                case "DEBUG":
                    _options = ["True", "False", "CANCEL"]
                    info = f"\nCURRENT VALUE: {_preferences["DEBUG"]}"
                    _choice = curses.wrapper(lambda stdscr: choice(stdscr, _options, menu="SELECT VALUE:", info=info))
                    if _choice == "CANCEL":
                        return
                    else:
                        _preferences["DEBUG"] = True if _choice == "True" else False
                case "LOGS":
                    _options = ["True", "False", "CANCEL"]
                    info = f"\nCURRENT VALUE: {_preferences["LOGS"]}"
                    _choice = curses.wrapper(lambda stdscr: choice(stdscr, _options, menu="SELECT VALUE:", info=info))
                    if _choice == "CANCEL":
                        return
                    else:
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
                    _preferences["PROMPT"] = _choice
                case "CANCEL":
                    return

            with open("preferences.json", 'w') as file:
                json.dump(_preferences, file, indent=4)
            clear()

        def choice(stdscr, choices, _banner: Optional[str] = banner, menu: Optional[str] = "MENU:", info: Optional[str] = ""):
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
            _options = ["LOAD BOTS", "FIRE BOTS", "PREFERENCES", "EXIT"]
            while True:
                _choice = curses.wrapper(lambda stdscr: choice(stdscr, _options))
                match _choice:
                    case "LOAD BOTS":
                        load_bots()
                    case "FIRE BOTS":
                        fire_bots()
                    case "PREFERENCES":
                        preferences()
                    case "EXIT":
                        exit()

        cli()
    except KeyboardInterrupt:
        main()


if __name__ == "__main__":
    main()
