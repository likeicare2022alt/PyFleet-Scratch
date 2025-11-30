# PyFleet Scratch
PyFleet Scratch is a CLI that allows you to flood the comments of scratch, (you do need a Huggingface [access token](https://huggingface.co/docs/hub/security-tokens), they are free, I will want to 
add an option that doesn't require AI)

## How to use
> [!NOTE]
> Requires python 3.12.x\
> For windows make sure you run `uv pip install windows-curses`

First you need to clone this repo, once that's done, go to the **PyFleetScratch** folder and run `uv sync` (install uv [here](https://docs.astral.sh/uv/#__tabbed_1_2) that will install all packages 
listed in the **uv.lock** file, then run this command `setx HF_API_KEY="your api key"` now you should be able to use `uv run cli.py` and a menu should show up after it's done initializing.
