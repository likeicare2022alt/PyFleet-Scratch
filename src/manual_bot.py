import scratchattach as scratch
import warnings
import time
from scratchattach.utils.exceptions import CommentPostFailure
from rich.console import Console
from typing import Optional
import json
from scratchattach.utils.exceptions import ProjectNotFound
import random

warnings.filterwarnings('ignore',
                        category=scratch.LoginDataWarning)  # Makes the LoginDataWarning from scratchattach not show
with open("preferences.json", 'r') as f:
    data = json.load(f)

PROJECT = data["TARGET"]
PROMPT = data["PROMPT"]
console = Console(force_terminal=True)
DEBUG = data["DEBUG"]
LOGS = data["LOGS"]
OUTPUTS = data["OUTPUTS"]


def get_new_values():
    """
    Gets the new values from preferences.json and sets the variables to those values
    :return:
    """
    global PROJECT, PROMPT, DEBUG, LOGS, data
    with open("preferences.json", 'r') as file:
        data = json.load(file)

    DEBUG = data["DEBUG"]
    LOGS = data["LOGS"]
    PROJECT = data["TARGET"]
    PROMPT = data["PROMPT"]


def mprint(*text, _type: Optional[str] = "DEBUG"):
    """
    Custom print function I made so I can hide debug logs

    :param _type:
    :param text:
    :return:
    """

    msg = " ".join(text)
    if LOGS:
        if _type == "DEBUG":
            if DEBUG:
                console.print(f"[green bold][{_type}][/green bold] {msg}")
        elif _type == "INFO":
            console.print(f"[bold white][{_type}][/bold white] [white]{msg}[/white]")
        elif _type == "ERROR":
            console.print(f"[red bold][{_type}][/red bold] {msg}")
        elif _type == "WARNING":
            console.print(f"[orange1 bold][{_type}][/orange1 bold] {msg}")
        else:
            console.print(f"[{_type}] {msg}")


def manual_bot(username, password, stop_event):
    """
    Creates a scratch bot

    :param stop_event:
    :param username:
    :param password:
    :return:
    """
    get_new_values()
    mprint("[bold]INITIALIZING[/bold]", _type="INFO")
    session = scratch.login(username, password)
    try:
        project = session.connect_project(PROJECT)
    except ProjectNotFound:
        mprint(
            "PROJECT NOT FOUND",
            _type="ERROR"
        )
        return
    comment_object = project.comments(limit=1, offset=0)[0]
    mprint("[bold green]INITIALIZED[/bold green]", _type="INFO")

    while not stop_event.is_set():
        _previous = comment_object.content
        _current = project.comments(limit=1, offset=0)[0].content

        time.sleep(1)  # Cooldown

        if not comment_object.content == project.comments(limit=1, offset=0)[0].content:
            comment_object = project.comments(limit=1, offset=0)[0]
            session.connect_user(comment_object.author_name).follow()

            try:
                project.post_comment(random.choice(OUTPUTS))
            except CommentPostFailure:
                mprint(
                    f"{username} is banned or muted",
                    _type="WARNING"
                )

            for _ in range(30):  # Checks for the thread stop event while waiting
                if stop_event.is_set():
                    return
                time.sleep(1)  # Makes sure messages don't count as spam

        comment_object = project.comments(limit=1, offset=0)[0]
