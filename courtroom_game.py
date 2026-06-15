import random
import json
import os

SAVE_FILE = "savegame.json"

# -------- PLAYER STATE --------
inventory = []
evidence = {}

player_stats = {
    "trust": 50,
    "logic": 0,
    "emotion": 0
}

player_level = 1
xp = 0
difficulty = "normal"

characters = {
    "Alex Rivera": {
        "role": "Client",
        "trait": "nervous",
        "secret": "was near library but denies entering"
    },
    "Jordan Lee": {
        "role": "Client",
        "trait": "aggressive",
        "secret": "hid something during incident"
    }
}

# -------- CORE --------
def pause():
    input("\n(Press Enter to continue)\n")

def show_instructions():
    print("\n=== COURTROOM RPG ===")
    print("Win cases by managing TRUST.")
    print("Collect evidence, survive twists, and choose wisely.\n")
    pause()

# -------- SAVE SYSTEM --------
def save_game():
    data = {
        "inventory": inventory,
        "evidence": evidence,
        "stats": player_stats,
        "level": player_level,
        "xp": xp
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)
    print("[Game Saved]")

def load_game():
    global inventory, evidence, player_stats, player_level, xp
    if not os.path.exists(SAVE_FILE):
        print("[No Save Found]")
        return
    with open(SAVE_FILE, "r") as f:
        data = json.load(f)
    inventory = data["inventory"]
    evidence = data["evidence"]
    player_stats = data["stats"]
    player_level = data["level"]
    xp = data["xp"]
    print("[Game Loaded]")

# -------- SYSTEMS --------
def add_evidence(name):
    inventory.append(name)
    evidence[name] = True
    print(f"[Evidence: {name}]")

def update_stats(t=0, l=0, e=0):
    player_stats["trust"] += t
    player_stats["logic"] += l
    player_stats["emotion"] += e

def gain_xp(amount):
    global xp, player_level
    xp += amount
    print(f"[+{amount} XP]")
    if xp >= player_level * 50:
        xp = 0
        player_level += 1
        print(f"LEVEL UP → {player_level}")

def random_twist():
    twists = [
        "Witness changes story.",
        "New evidence appears.",
        "Client reveals secret.",
        "Prosecution surprises you."
    ]
    print("TWIST:", random.choice(twists))

# -------- ENDING --------
def ending():
    t = player_stats["trust"]

    if difficulty == "hard":
        t -= 10
    elif difficulty == "easy":
        t += 10

    print("\nFINAL TRUST:", t)

    if t >= 75:
        print("NOT GUILTY")
        gain_xp(30)
    elif t >= 50:
        print("HUNG JURY")
        gain_xp(15)
    else:
        print("GUILTY")
        gain_xp(5)

    pause()

# -------- CASES --------

def reset():
    player_stats["trust"] = 50
    inventory.clear()
    evidence.clear()

def case_1():
    reset()
    print("\nCASE 1: STOLEN LAPTOP")

    c = input("1 Aggressive 2 Logical 3 Emotional > ")
    if c == "2": update_stats(t=10)

    add_evidence("CCTV")
    random_twist()
    ending()

def case_2():
    reset()
    print("\nCASE 2: CAFETERIA INCIDENT")

    c = input("1 Self-defense 2 Witness 3 Footage > ")
    if c == "3": update_stats(t=10)

    random_twist()
    ending()

def case_3():
    reset()
    print("\nCASE 3: STOLEN IDENTITY")

    c = input("1 Transactions 2 IP logs 3 Interview > ")
    if c == "2": update_stats(t=12)

    add_evidence("IP mismatch")
    random_twist()
    ending()

def case_4():
    reset()
    print("\nCASE 4: CHEATING SCANDAL")

    c = input("1 Logs 2 Teacher 3 Students > ")
    if c == "1": update_stats(t=10)

    random_twist()
    ending()

def case_5():
    reset()
    print("\nCASE 5: LOCKER THEFT")

    c = input("1 Janitor 2 Athlete 3 Outsider > ")
    if c == "2": update_stats(t=10)

    random_twist()
    ending()

def case_6():
    reset()
    player_stats["trust"] = 40
    print("\nCASE 6: FALSE ACCUSATION")

    c = input("1 Trust client 2 Investigate 3 Challenge > ")
    if c == "2": update_stats(t=15)

    random_twist()
    ending()

def case_7():
    reset()
    print("\nCASE 7: CYBERBULLYING")

    c = input("1 Messages 2 IP 3 Interview > ")
    if c == "2": update_stats(t=12)

    random_twist()
    ending()

# -------- MENU --------
def menu():
    while True:
        print("\n=== MENU ===")
        print("1 Case1")
        print("2 Case2")
        print("3 Case3")
        print("4 Case4")
        print("5 Case5")
        print("6 Case6")
        print("7 Case7")
        print("8 Save")
        print("9 Load")
        print("10 Exit")

        c = input("> ")

        if c == "1": case_1()
        elif c == "2": case_2()
        elif c == "3": case_3()
        elif c == "4": case_4()
        elif c == "5": case_5()
        elif c == "6": case_6()
        elif c == "7": case_7()
        elif c == "8": save_game()
        elif c == "9": load_game()
        elif c == "10": break
        else: print("Invalid")

# -------- START --------
if __name__ == "__main__":
    show_instructions()
    menu()