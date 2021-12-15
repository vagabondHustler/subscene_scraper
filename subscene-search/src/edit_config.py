import json

from src.sos import root_directory_file
from src.config import get

# update config.json
def update_json(key: str, value) -> None:
    with open(root_directory_file("data/config.json"), "r+", encoding="utf-8") as f:
        data = json.load(f)
        data[key] = value
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()


# set language
def select_language() -> None:
    languages = get("languages")
    print("\n")
    print("[Fully supported languages]")
    for num, value in enumerate(languages):
        if num < 10:
            print(f"{num}.  {value}")
        else:
            print(f"{num}. {value}")
    print("\n")
    print("[Supported languages] - Slower search times")
    print("Visit: https://u.subscene.com/filter")
    print("\n")
    while True:
        answer = int(input("Enter number for corresponding subtitle: "))
        for num, value in enumerate(languages):
            if answer == num:
                update_json("language", value)
                print("\n\n")
                return
            elif answer != num and num >= len(languages):
                print("Not a valid number")
                print("Enter custom language from https://u.subscene.com/filter ?")
                choice = input("[y]/[N]: ")
                if choice.lower() == "y":
                    print("Example: English")
                    new_answer = input("Enter language: ")
                    custom_answer = f"{new_answer}, en"
                    update_json("language", custom_answer)
                    print("\n\n")
                    return


# set precentage threshold
def select_precentage_pass() -> None:
    while True:
        value = int(input("Enter number between 1-100: "))
        if value <= 100:
            break
        else:
            print("Must be a number between 1-100")
    update_json("precentage_pass", value)


# set if terminal is hidden or shown while searching
def select_terminal_focus() -> None:
    while True:
        answer = input("Show terminal while searching? [y/n]: ")
        if answer.lower() == "y":
            value = "True"
            break
        if answer.lower() == "n":
            value = "False"
            break
        else:
            print("Please enter f or m")
    update_json("terminal_focus", value)


def select_cm_icon() -> None:
    while True:
        answer = input("Icon in context menu [y/n]: ")
        if answer.lower() == "y":
            value = "True"
            break
        if answer.lower() == "n":
            value = "False"
            break
        else:
            print("Please enter y or n")
    update_json("context_menu_icon", value)
