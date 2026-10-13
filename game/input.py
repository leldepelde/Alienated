
_NAMED = {
    "KEY_UP": "up",
    "KEY_DOWN": "down",
    "KEY_LEFT": "left",
    "KEY_RIGHT": "right",
    "KEY_ENTER": "enter",
    "KEY_ESCAPE": "esc",
    "KEY_BACKSPACE": "backspace",
}


def normalize(key) -> str:
    if key.is_sequence:
        return _NAMED.get(key.name, (key.name or "").lower())
    if key == " ":
        return "space"
    if key in ("\n", "\r"):
        return "enter"
    return str(key).lower()


# Movement keys -> (dx, dy). Arrow keys and WASD both work.
MOVES = {
    "up": (0, -1), "w": (0, -1),
    "down": (0, 1), "s": (0, 1),
    "left": (-1, 0), "a": (-1, 0),
    "right": (1, 0), "d": (1, 0),
}

CONFIRM_KEYS = ("enter", "space", "e", "b")
