
import random
import time

from ..characters import CHARACTERS
from ..input import CONFIRM_KEYS
from ..ui import center, color
from .base import Scene

PHRASES = [
    "WE MEAN NO HARM",
    "WHO SENT YOU HERE",
    "STOP YOUR ENGINES",
    "ARE YOU LIKE US",
    "WHY DID EARTH GO QUIET",
    "YOU ARE NOT WELCOME",
]

TIME_PER_CHAR_BASE = 0.9   
TIME_PER_CHAR_BONUS = 0.6   
TIME_FLAT_BONUS = 3.0       # flat buffer 

MISS_PENALTY_BASE = 0.6     
MISS_PENALTY_MIN = 0.2      
HIT_BONUS = 0.2             # seconds gained per correct key
#tweeak fuzz for difficulty !
FUZZ_WIDTH = 60             
FUZZ_ROWS = 2               # rows of pure static above AND below 
FUZZ_SHIMMER = 0.12         
FUZZ_TICK = 0.08           
FLICKER_BASE = 0.22        
FLICKER_MIN = 0.06         
NOISE_SYMBOLS = "#@%$&*?!~^/\\|<>=+;:"
NOISE_LETTERS = "XQJZKVWDS"  


def noise_char():
    pool = NOISE_LETTERS if random.random() < 0.15 else NOISE_SYMBOLS
    return random.choice(pool)


class SignalDecodeMinigame(Scene):
    def __init__(self, game, helper_id=None, title="SIGNAL DECODER", on_done=None):
        super().__init__(game)
        self.title = title
        self.on_done = on_done
        self.now = time.perf_counter
        assist = game.state.assist(helper_id) if helper_id in CHARACTERS else 0.0
        self.helper = CHARACTERS.get(helper_id)

        self.target = random.choice(PHRASES)
        per_char = TIME_PER_CHAR_BASE + TIME_PER_CHAR_BONUS * assist
        self.time_total = len(self.target) * per_char + TIME_FLAT_BONUS
        self.miss_penalty = MISS_PENALTY_BASE - (MISS_PENALTY_BASE - MISS_PENALTY_MIN) * assist
        self.flicker = FLICKER_BASE - (FLICKER_BASE - FLICKER_MIN) * assist

        self.top = [self.noise_row() for _ in range(FUZZ_ROWS)]
        self.bottom = [self.noise_row() for _ in range(FUZZ_ROWS)]
        self.pad_left = (FUZZ_WIDTH - len(self.target)) // 2
        self.pad_right = FUZZ_WIDTH - len(self.target) - self.pad_left
        self.left = self.noise_row(self.pad_left)
        self.right = self.noise_row(self.pad_right)
        self.glitch = set()            #  of the message currently flickering
        self.fuzz_timer = 0.0

        self.typed = 0
        self.time_left = self.time_total
        self.phase = "ready"           # ready -> playing -> result
        self.flash = None
        self.flash_until = 0.0
        self.success = None

    # fuzzy wuzzies
    @staticmethod
    def noise_row(n=FUZZ_WIDTH):
        return [noise_char() for _ in range(n)]

    @staticmethod
    def shimmer(row):
        for i in range(len(row)):
            if random.random() < FUZZ_SHIMMER:
                row[i] = noise_char()

    def tick_fuzz(self):
        for row in self.top + self.bottom + [self.left, self.right]:
            self.shimmer(row)
        # letters we haven't reached yet may glitch; the one we need is always clear
        self.glitch = {i for i in range(self.typed + 1, len(self.target))
                       if self.target[i] != " " and random.random() < self.flicker}

    # ---- input -------------------------------------------------------------
    def handle_key(self, key):
        if self.phase == "ready":
            if key in CONFIRM_KEYS:
                self.phase = "playing"
            elif key == "esc":
                self.leave(False)
            return
        if self.phase == "playing":
            if key == "esc":
                self.leave(False)
                return
            if key == "backspace":
                self.typed = max(0, self.typed - 1)
                return
            ch = " " if key == "space" else key
            if len(ch) != 1:
                return
            wanted = self.target[self.typed].lower() if self.typed < len(self.target) else None
            if wanted is not None and ch.lower() == wanted:
                self.typed += 1
                self.time_left = min(self.time_total, self.time_left + HIT_BONUS)
                self.flash, self.flash_until = "hit", self.now() + 0.15
                if self.typed >= len(self.target):
                    self.finish(True)
            else:
                self.time_left -= self.miss_penalty
                self.flash, self.flash_until = "miss", self.now() + 0.15
            return
        if self.phase == "result" and key in CONFIRM_KEYS:
            self.leave(self.success)

    def leave(self, success):
        self.game.pop()
        if self.on_done:
            self.on_done(success)

    def finish(self, success):
        self.success = success
        self.phase = "result"

    def update(self, dt):
        self.fuzz_timer -= dt
        if self.fuzz_timer <= 0:
            self.fuzz_timer = FUZZ_TICK
            self.tick_fuzz()
        if self.phase != "playing":
            return
        self.time_left -= dt
        if self.time_left <= 0:
            self.time_left = 0
            self.finish(False)

    def fuzz_line(self, row):
        t = self.term
        return "".join(t.color(8)(c) for c in row)

    def phrase_line(self):
        t = self.term
        out = self.fuzz_line(self.left)
        for i, c in enumerate(self.target):
            if self.phase == "result" and not self.success:
                out += t.color(8)(noise_char())          #  dissolvedddd
            elif i < self.typed:
                out += color(t, "black_on_green", c)
            elif i == self.typed and self.phase == "playing":
                out += color(t, "black_on_yellow", c)
            elif i in self.glitch and self.phase == "playing":
                out += color(t, "black_on_cyan", noise_char())
            else:
                out += color(t, "black_on_cyan", c)
        return out + self.fuzz_line(self.right)

    def draw(self, width, height):
        t = self.term
        lines = ["", center(t, t.bold(f"=== {self.title} ==="), width), ""]

        if self.phase == "ready":
            lines.append(center(t, "An alien transmission is coming through - buried in static.", width))
            lines.append(center(t, "The real message will be highlighted. Type it exactly", width))
            lines.append(center(t, "before the window closes. Letters may flicker; ignore the fuzz.", width))
            lines.append("")
            for row in self.top:
                lines.append(center(t, self.fuzz_line(row), width))
            lines.append(center(t, self.fuzz_line(self.noise_row(self.pad_left)) +
                                color(t, "black_on_cyan", "?" * len(self.target)) +
                                self.fuzz_line(self.noise_row(self.pad_right)), width))
            for row in self.bottom:
                lines.append(center(t, self.fuzz_line(row), width))
            lines.append("")
            if self.helper:
                lines.append(center(
                    t, f"{self.helper.name} is helping ({self.time_total:.0f}s to work with)", width))
            lines += ["", center(t, t.bold_yellow("Press ENTER to start"), width)]
            return lines

        bar_w = 40
        frac = 0 if self.time_total <= 0 else max(0.0, self.time_left / self.time_total)
        filled = int(round(frac * bar_w))
        bar_color = "bold_green" if frac > 0.5 else "bold_yellow" if frac > 0.2 else "bold_red"
        bar = "[" + getattr(t, bar_color)("█" * filled) + t.color(8)("░" * (bar_w - filled)) + "]"
        lines.append(center(t, bar, width))
        lines.append("")

        for row in self.top:
            lines.append(center(t, self.fuzz_line(row), width))
        lines.append(center(t, self.phrase_line(), width))
        for row in self.bottom:
            lines.append(center(t, self.fuzz_line(row), width))
        lines.append("")

        if self.phase == "playing":
            if self.flash and self.now() < self.flash_until:
                msg = t.bold_green("signal lock") if self.flash == "hit" else t.bold_red("static burst")
                lines.append(center(t, msg, width))
            else:
                lines.append("")
            lines.append(center(t, "Type the highlighted message - BACKSPACE to fix a mistake", width))
        else:
            if self.success:
                lines.append(center(t, t.bold_green("TRANSLATION LOCKED"), width))
            else:
                lines.append(center(t, t.bold_red("SIGNAL LOST"), width))
            lines.append(center(t, "[ENTER] continue", width))
        return lines