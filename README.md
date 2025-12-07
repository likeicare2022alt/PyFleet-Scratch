# PyFleet Scratch
> [!WARNING]
> Use a VPN and an email faker, you can get IP banned and email banned from using this\
> I recommend [Proton VPN](https://protonvpn.com/) and [FakeMail](https://www.fakemail.net/) because they're both free

PyFleet Scratch is a CLI that allows you to flood the comments of scratch

> [!NOTE]
> To use AI features you need to create a huggingface access token, you can get one [here](https://huggingface.co/settings/tokens)

## Setup
> [!NOTE]
> Requires python 3.12.x because of PyTorch\
> Make sure you have [uv](https://docs.astral.sh/uv/#installation) installed, you need it to run this project

### Unix
First you need to clone this repo, once that's done, go to the `PyFleetScratch` folder and run `uv sync`.\
That will install all packages listed in the `uv.lock` file.\
Now to activate the venv, run `source .venv/bin/activate`.
### Windows
> [!NOTE]
> You must install and additional package called `windows-curses`\
> To install, use `uv add windows-curses`

First you need to clone this repo, once that's done, go to the `PyFleetScratch` folder and run `uv sync`.\
That will install all packages listed in the `uv.lock` file.

## Start the Program
To start the program make sure you have **all** required packages installed for windows users install `windows-curses`\
Now once everything is done, use the `uv run cli.py` command inside of `PyFleet-Scratch/src/`

## Formatting a CSV File
When uploading a CSV file filled with accounts you need to format it like this
```text
username,password
username,password
username,password
```
Then you can upload it