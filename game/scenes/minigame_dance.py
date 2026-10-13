
import math
import time

from ..characters import CHARACTERS
from ..input import CONFIRM_KEYS
from ..ui import center, color
from .base import Scene

SLOT = 0.25
CHART = [
    "L.D.U.R.",
    "L.D.U.R.",
    "LRLR.D.U",
    "U.D.L.R.",
    "LDUR....",
    "RUDL....",
    "L.R.L.R.",
    "D.U.D.U.",
    "LDLDRURU",
    "L.D.U.R.",
    "RLRL.DU.",
    "U.U.D.D.",
    "LDUR.RUD",
    "L.R.L.R.",
    "ULDR....",
    "L.D.U.R.",
]
LEAD_IN = 2.0        
COUNTDOWN = 3.0     
LOOKAHEAD = 1.5      
TAIL = 1.5           

#  timing + scoring
PERFECT_WINDOW = 0.12    # seconds either side of the perfect moment
GOOD_WINDOW = 0.25
POINTS = {"perfect": 100, "good": 60}

# ----------------------------------- the look
LANE_W = 7                       #
PANEL_W = LANE_W * 4 + 2         
RIGHT_W = 46
GAP = 2
TOTAL_W = PANEL_W + GAP + RIGHT_W

LANES = [
    {"name": "left",  "keys": ("left", "a"),  "color": "magenta", "art": [" /   ", "<====", " \\   "]},
    {"name": "down",  "keys": ("down", "s"),  "color": "cyan",    "art": ["  |  ", " \\|/ ", "  v  "]},
    {"name": "up",    "keys": ("up", "w"),    "color": "green",   "art": ["  ^  ", " /|\\ ", "  |  "]},
    {"name": "right", "keys": ("right", "d"), "color": "red",     "art": ["   \\ ", "====>", "   / "]},
]
KEY_TO_LANE = {k: i for i, lane in enumerate(LANES) for k in lane["keys"]}
LETTER_TO_LANE = {"L": 0, "D": 1, "U": 2, "R": 3}
ART_H = 3

# the posesssssssss
POSES = {
    "idle1": ["   O   ", "  /|\\  ", " / | \\ ", "   |   ", "  / \\  ", " /   \\ "],
    "idle2": ["   O   ", "  \\|/  ", "   |   ", "   |   ", "  / \\  ", "  | |  "],
    "left":  ["   O   ", " --|\\  ", "   |   ", "  /|   ", " /  \\  ", "/    \\ "],
    "right": ["   O   ", "  /|-- ", "   |   ", "   |\\  ", "  /  \\ ", " /    \\"],
    "up":    ["\\  O  /", " \\ | / ", "  \\|/  ", "   |   ", "  / \\  ", " /   \\ "],
    "down":  ["       ", "   O   ", " --|-- ", "   |   ", "  /_\\  ", " /   \\ "],
    "miss":  ["       ", "   X   ", "  _|_  ", "   |   ", "  / \\  ", " /   \\ "],
}
LANE_POSE = ["left", "down", "up", "right"]
POSE_H = 6

JUDGE_TEXT = {"perfect": "P E R F E C T", "good": "G O O D", "miss": "M I S S"}
JUDGE_COLOR = {"perfect": "bold_yellow", "good": "bold_green", "miss": "bold_red"}


def build_notes():
    notes = []
    for i, ch in enumerate("".join(CHART)):
        if ch in LETTER_TO_LANE:
            notes.append({"lane": LETTER_TO_LANE[ch], "t": LEAD_IN + i * SLOT, "state": None})
    return notes


def grade_for(accuracy):
    for letter, need in (("S", 0.95), ("A", 0.85), ("B", 0.70), ("C", 0.50)):
        if accuracy >= need:
            return letter
    return "D"


def fit(term, text, width):
    """Center `text` (may contain colors) in exactly `width` columns."""
    extra = max(0, width - term.length(text))
    left = extra // 2
    return " " * left + text + " " * (extra - left)


class DanceScene(Scene):
    def __init__(self, game, helper_id=None, title="DANCE FLOOR", on_done=None):
        super().__init__(game)
        self.title = title
        self.on_done = on_done
        self.now = time.perf_counter      
        assist = game.state.assist(helper_id) if helper_id in CHARACTERS else 0.0
        self.scale = 1.0 + 0.4 * assist       # better relationship = wider windows
        self.helper = CHARACTERS.get(helper_id)

        self.notes = build_notes()
        self.last_note_time = max(n["t"] for n in self.notes)
        self.phase = "ready"                  
        self.t0 = 0.0                        
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.counts = {"perfect": 0, "good": 0, "miss": 0}
        self.meter = 0.5
        self.pose = "idle1"
        self.pose_until = 0.0
        self.flash = [0.0] * 4                # clock time each lane stops flashing
        self.judgment = None
        self.judgment_until = 0.0
        self.result = None

    #  
    def song_time(self):
        return self.now() - self.t0

    def start(self):
        self.phase = "playing"
        self.t0 = self.now() + COUNTDOWN

    def set_pose(self, name, seconds=0.3):
        self.pose = name
        self.pose_until = self.now() + seconds

    def show_judgment(self, kind):
        self.judgment = kind
        self.judgment_until = self.now() + 0.7

    def leave(self, success):
        self.game.pop()
        if self.on_done:
            self.on_done(success)

    # -------------
    def handle_key(self, key):
        if self.phase == "ready":
            if key in CONFIRM_KEYS:
                self.start()
            elif key == "esc":
                self.leave(False)
        elif self.phase == "playing":
            if key in KEY_TO_LANE:
                self.press(KEY_TO_LANE[key])
            elif key == "esc":
                self.leave(False)
        elif self.phase == "result" and key in CONFIRM_KEYS:
            self.leave(self.result["passed"])

    def press(self, lane):
        st = self.song_time()
        self.flash[lane] = self.now() + 0.12
        self.set_pose(LANE_POSE[lane])
        if st < 0:
            return                              # still counting down
        best, best_err = None, None
        for n in self.notes:
            if n["lane"] == lane and n["state"] is None:
                err = abs(n["t"] - st)
                if best is None or err < best_err:
                    best, best_err = n, err
        if best is None or best_err > GOOD_WINDOW * self.scale:
            self.meter = max(0.0, self.meter - 0.02)     # stray press
            return
        kind = "perfect" if best_err <= PERFECT_WINDOW * self.scale else "good"
        best["state"] = kind
        self.counts[kind] += 1
        self.combo += 1
        self.max_combo = max(self.max_combo, self.combo)
        self.score += POINTS[kind] + 2 * self.combo
        self.meter = min(1.0, self.meter + (0.03 if kind == "perfect" else 0.015))
        self.show_judgment(kind)

    
    def update(self, dt):
        if self.phase != "playing":
            return
        st = self.song_time()
        for n in self.notes:
            if n["state"] is None and st - n["t"] > GOOD_WINDOW * self.scale:
                n["state"] = "miss"
                self.counts["miss"] += 1
                self.combo = 0
                self.meter = max(0.0, self.meter - 0.06)
                self.show_judgment("miss")
                if self.now() >= self.pose_until:
                    self.set_pose("miss", 0.4)
        if st > self.last_note_time + TAIL:
            total = len(self.notes)
            acc = (self.counts["perfect"] + 0.6 * self.counts["good"]) / total
            self.result = {"grade": grade_for(acc), "accuracy": acc, "passed": acc >= 0.5}
            self.phase = "result"

    def current_pose(self):
        now = self.now()
        if self.phase == "result":
            return "up" if self.result["passed"] else "miss"
        if now < self.pose_until:
            return self.pose
        return "idle1" if int(now * 2) % 2 == 0 else "idle2"     # sway to the beat ooooh yeah boom boom pow woohoo

    def style(self, name, text):
        return color(self.term, name, text)

    def lane_cells(self, R):
        """grid[lane][row] = styled 7-char string for the arrow panel."""
        t = self.term
        now = self.now()
        st = self.song_time()
        blank = " " * LANE_W
        grid = [[blank] * R for _ in LANES]
        bottom = R - ART_H                               
        speed = bottom / LOOKAHEAD                   

        # falling arrows
        for n in self.notes:
            if n["state"] in ("perfect", "good"):
                continue
            y = int(round(bottom - (n["t"] - st) * speed))
            lane = LANES[n["lane"]]
            for i, row in enumerate(lane["art"]):
                r = y + i
                if 0 <= r < R:
                    base = "bold_" + lane["color"]
                    if n["state"] == "miss":
                        base = "white"                    
                    grid[n["lane"]][r] = self.style(base, " " + row + " ")

        # receptors (the "hit here" arrows) drawn on top
        for li, lane in enumerate(LANES):
            lit = now < self.flash[li]
            for i, row in enumerate(lane["art"]):
                text = " " + row + " "
                if lit:
                    grid[li][bottom + i] = self.style("bold_black_on_" + lane["color"], text)
                else:
                    grid[li][bottom + i] = t.color(8)(text)
        return grid

    def right_column(self, R):
        t = self.term
        rows = [""] * R
        st = self.song_time()

        if self.phase == "ready":
            rows[1] = t.bold("Hit the arrows as they reach the bottom!")
            rows[2] = "Arrows or WASD   -   ESC to quit"
            rows[3] = t.bold_yellow("Press ENTER to start")
            if self.helper:
                rows[4] = f"{self.helper.name} is helping (timing is {int((self.scale - 1) * 100)}% more forgiving)"
        elif self.phase == "result":
            r = self.result
            rows[0] = t.bold("=== RESULTS ===")
            rows[1] = t.bold_yellow(f"Grade: {r['grade']}") if r["passed"] else t.bold_red(f"Grade: {r['grade']}")
            rows[2] = f"Score {self.score}   Max combo {self.max_combo}"
            rows[3] = (f"Perfect {self.counts['perfect']}   Good {self.counts['good']}   "
                       f"Miss {self.counts['miss']}")
            rows[4] = t.bold("[ENTER] continue")
        else:
            if st < 0:
                n = int(math.ceil(-st))
                rows[2] = t.bold_yellow(f"- {n} -")
            else:
                if self.combo >= 2:
                    rows[0] = t.bold(f"COMBO {self.combo}")
                if self.judgment and self.now() < self.judgment_until:
                    rows[2] = self.style(JUDGE_COLOR[self.judgment], JUDGE_TEXT[self.judgment])

        # the stick figure + stage floor
        pose = POSES[self.current_pose()]
        width = max(len(line) for line in pose)
        top = R - 1 - POSE_H
        for i, line in enumerate(pose):
            rows[top + i] = self.style("bold_white", line.ljust(width))
        rows[R - 1] = t.color(8)("=" * 30)
        return [fit(t, row, RIGHT_W) for row in rows]

    def draw(self, width, height):
        t = self.term
        R = max(12, min(24, height - 7))
        pad = " " * max(0, (width - TOTAL_W) // 2)
        gap = " " * GAP
        blank_right = " " * RIGHT_W

        lines = [center(t, t.bold(f"=== {self.title} ==="), width)]

        # groove meter (red bar, top left) + score (top right)
        inner = PANEL_W - 2
        filled = int(round(self.meter * inner))
        bar = "[" + self.style("bold_red", "█" * filled) + t.color(8)("░" * (inner - filled)) + "]"
        lines.append(pad + bar + gap + fit(t, t.bold(f"SCORE {self.score:07d}"), RIGHT_W))

        grid = self.lane_cells(R)
        right = self.right_column(R)
        lines.append(pad + "╔" + "═" * inner + "╗")
        for r in range(R):
            panel = "║" + "".join(grid[li][r] for li in range(4)) + "║"
            lines.append(pad + panel + gap + right[r])
        lines.append(pad + "╚" + "═" * inner + "╝")

        # song progress + hints
        total = self.last_note_time + TAIL
        frac = 0.0 if self.phase == "ready" else max(0.0, min(1.0, self.song_time() / total))
        if self.phase == "result":
            frac = 1.0
        n = int(frac * inner)
        lines.append(pad + "[" + "#" * n + "-" * (inner - n) + "]" + gap +
                     fit(t, "Move: arrows / WASD    Quit: ESC", RIGHT_W))
        return lines
