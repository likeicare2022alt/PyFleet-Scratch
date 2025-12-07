import scratchattach as scratch
from scratchattach.utils.exceptions import LoginFailure
from rich.console import Console

console = Console()


def check(username, password):
    try:
        session = scratch.login(username, password)
        mute = session.mute_status
        if not mute == {}:
            console.print(f"[bold orange1]{username} has been muted[/bold orange1]")
        else:
            console.print(f"[bold green]{username} has not been affected by any moderation[/bold green]")
            return [username, password]
    except LoginFailure:
        console.print(f"[bold red]{username} has been banned[/bold red]")
