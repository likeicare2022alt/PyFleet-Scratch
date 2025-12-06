import scratchattach as scratch
from huggingface_hub import InferenceClient
import warnings
import time
from scratchattach.utils.exceptions import CommentPostFailure
from huggingface_hub.utils import HfHubHTTPError
from rich.console import Console
from typing import Optional
import json
from scratchattach.utils.exceptions import ProjectNotFound
import html
print("INITIALIZING PyTorch")
from transformers import pipeline

warnings.filterwarnings('ignore',
                        category=scratch.LoginDataWarning)  # Makes the LoginDataWarning from scratchattach not show
with open("config.json", 'r') as f:
    data = json.load(f)


moderator = pipeline("text-classification", model="unitary/toxic-bert")  # Moderator for the AI's output

PROJECT = data["TARGET"]
PROMPT = data["PROMPT"]
console = Console(force_terminal=True)
DEBUG = data["DEBUG"]
LOGS = data["LOGS"]
API_KEY = data["API KEY"]
RATELIMIT = data["RATELIMIT"]


def get_new_values():
    """
    Gets the new values from preferences.json and sets the variables to those values
    :return:
    """
    global PROJECT, PROMPT, DEBUG, LOGS, API_KEY, RATELIMIT, data
    with open("config.json", 'r') as file:
        data = json.load(file)

    DEBUG = data["DEBUG"]
    LOGS = data["LOGS"]
    PROJECT = data["TARGET"]
    PROMPT = data["PROMPT"]
    API_KEY = data["API KEY"]
    RATELIMIT = data["RATELIMIT"]


def client():
    return InferenceClient(api_key=API_KEY)


def moderate(text: str) -> bool:
    results = moderator(text)
    return any(r["label"] in ["toxic", "sexual", "violent"] and r["score"] > 0.7 for r in
               results)  # Returns the score of these categories


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


def generate(content: str):
    """
    Generates an AI response and returns it

    :param content:
    :return:
    """

    return client().chat.completions.create(
        model="meta-llama/Llama-3.1-8B-Instruct",
        messages=[
            {
                "role": "user",
                "content": content
            }
        ],
    ).choices[0].message


def bot(username, password, stop_event):
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
        _commentBool = comment_object.content == project.comments(limit=1, offset=0)[
            0].content  # The comment boolean, for debugging
        _previous = comment_object.content
        _current = project.comments(limit=1, offset=0)[0].content
        mprint(
            f"PREVIOUS: [bold green]{_previous}[/bold green] CURRENT: [bold green]{_current}[/bold green] BOOL: [bold green]{_commentBool}[/bold green]",
            _type="DEBUG"
        )

        time.sleep(1)  # Cooldown

        if not comment_object.content == project.comments(limit=1, offset=0)[0].content:
            comment_object = project.comments(limit=1, offset=0)[0]
            comment = comment_object.content
            session.connect_user(comment_object.author_name).follow()

            try:
                response = generate(
                    PROMPT.replace("%c", html.unescape(comment).strip()).replace("%u", comment_object.author_name)
                ).content
            except HfHubHTTPError:
                mprint(
                    "Failed to generate! You have probably ran out of credits",
                    _type="ERROR"
                )
                stop_event.set()
                return

            mprint(
                f"INPUT: [bold green]{comment}[/bold green] OUTPUT: [bold green]{response[0:500]}[/bold green]",
                _type="DEBUG"
            )

            try:
                if not moderate(response):
                    mprint(
                        f"REPLIED TO {comment_object.author_name} WITH {response}",
                        _type="INFO"
                    )
                    project.reply_comment(response[0:500].strip(), parent_id=comment_object.id)
                else:
                    mprint(
                        f"moderate function returned true, bot: {session.username}",
                        _type="ERROR"
                    )
            except CommentPostFailure:
                if session.banned:
                    mprint(
                        f"[bold red]{session.username} has been banned[/bold red]",
                        _type="WARNING"
                    )
                else:
                    mprint(
                        f"{session.username} has been muted",
                        _type="WARNING"
                    )

            for _ in range(RATELIMIT):
                if stop_event.is_set():
                    return
                time.sleep(1)  # Makes sure messages don't count as spam

        comment_object = project.comments(limit=1, offset=0)[0]
