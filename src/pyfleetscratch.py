import os
import json

if __name__ == "__main__":
    # The default contents for 'config.json'
    __preferences = {
        "PROMPT": "PROMPT",
        "DEBUG": True,
        "LOGS": True,
        "TARGET": 1,
        "BOT TYPE": "MANUAL",
        "OUTPUTS": [],
        "BOTS": [],
        "API KEY": "",
        "RATELIMIT": 30
    }
    # Check if 'config.json' exists, if not it creates one
    if not os.path.exists("config.json"):
        print("CREATING config.json")
        with open('config.json', 'w') as f:
            json.dump(__preferences, f, indent=2)

    print("INITIALIZING PyFleet Scratch")
    from cli import main
    main()
