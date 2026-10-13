from dataclasses import dataclass


@dataclass
class Character:
    id: str                 # short id 
    name: str               # name shown on screen
    role: str
    start_relationship: int = 10   # 0-100
    color: str = "white"    # blessed color name for da name tag


CHARACTERS = {
    "vera": Character("vera", "Vera", "Captain", 10, "magenta"),
    "rex": Character("rex", "Rex", "Engineer", 10, "cyan"),
    "alien": Character("alien", "Alien", "Mars Captain", 10, "green")
} #zeepy zorpy zeepy weepy 
