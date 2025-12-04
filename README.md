# PyFleet Scratch
PyFleet Scratch is a CLI that allows you to flood the comments of scratch, (you do need a Huggingface [access token](https://huggingface.co/docs/hub/security-tokens), they are free, there is a version that doesn't require AI, just go to preferences, select bot type, and set it to manual, then add comment outputs by going to preferences, outputs)

## Setup
> [!NOTE]
> Requires python 3.12.x because of PyTorch

### Unix
First you need to clone this repo, once that's done, go to the `PyFleetScratch` folder and run `uv sync` (install uv [here](https://docs.astral.sh/uv/#installation)).\
That will install all packages listed in the `uv.lock` file.\
Now to activate the venv, run `source .venv/bin/activate`.
### Windows
> [!NOTE]
> You must install and additional package called `windows-curses`\
> To install use `uv add windows-curses`

First you need to clone this repo, once that's done, go to the `PyFleetScratch` folder and run `uv sync` (install uv [here](https://docs.astral.sh/uv/#__tabbed_1_2)).\
That will install all packages listed in the `uv.lock` file.

## Start the Program
To start the program make sure you have **all** required packages installed for windows users install `windows-curses`\
Now once everything is done, use the `uv run cli.py` command inside of `PyFleet-Scratch/src/`
