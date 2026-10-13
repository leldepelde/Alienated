
import random

from ..characters import CHARACTERS
from ..input import CONFIRM_KEYS
from ..ui import center
from .base import Scene

BAR_WIDTH = 44
ROUNDS = 3
NEEDED = 2


def difficulty(assist: float) -> dict:
    """assist is 0.0..1.0 (see GameState.assist)."""
    return {
        "zone": round(3 + 11 * assist),      # green zone: 3..14 characters wide
        "speed": 38 - 20 * assist,           # marker speed in chars/second
    }


class TimingMinigame(Scene):
    def __init__(self, game, helper_id, title="MINIGAME", on_done=None):
        super().__init__(game)
        self.helper = CHARACTERS[helper_id]
        self.title = title
        self.on_done = on_done
        self.diff = difficulty(game.state.assist(helper_id))
        self.round = 0
        self.hits = 0
        self.phase = "playing"      # playing -> pause -> (next round | result)
        self.pause_timer = 0.0
        self.last_hit = False
        self.start_round()

    def start_round(self):
        self.pos = 0.0
        self.dir = 1
        self.zone_start = random.randint(4, BAR_WIDTH - self.diff["zone"] - 4)

    def in_zone(self):
        return self.zone_start <= int(self.pos) < self.zone_start + self.diff["zone"]

    def handle_key(self, key):
        if self.phase == "playing" and key in CONFIRM_KEYS:
            self.last_hit = self.in_zone()
            self.hits += self.last_hit
            self.round += 1
            self.phase, self.pause_timer = "pause", 0.8
        elif self.phase == "result" and key in CONFIRM_KEYS:
            self.game.pop()
            if self.on_done:
                self.on_done(self.hits >= NEEDED)

    def update(self, dt):
        if self.phase == "playing":
            self.pos += self.dir * self.diff["speed"] * dt
            if self.pos >= BAR_WIDTH - 1:
                self.pos, self.dir = BAR_WIDTH - 1, -1
            elif self.pos <= 0:
                self.pos, self.dir = 0, 1
        elif self.phase == "pause":
            self.pause_timer -= dt
            if self.pause_timer <= 0:
                if self.round >= ROUNDS:
                    self.phase = "result"
                else:
                    self.start_round()
                    self.phase = "playing"

    def draw(self, width, height):
        t = self.term
        rel = self.game.state.rel(self.helper.id)
        bar = ""
        for i in range(BAR_WIDTH):
            if self.phase == "playing" and i == int(self.pos):
                bar += t.bold_yellow("|")
            elif self.phase == "pause" and i == int(self.pos):
                bar += (t.bold_green("|") if self.last_hit else t.bold_red("|"))
            elif self.zone_start <= i < self.zone_start + self.diff["zone"]:
                bar += t.green("█")
            else:
                bar += t.color(8)("░")

        lines = ["", "", center(t, t.bold(f"=== {self.title} ==="), width), ""]
        lines.append(center(t, f"{self.helper.name} is helping (relationship {rel}/100)", width))
        lines.append(center(t, f"Green zone: {self.diff['zone']} wide", width))
        lines += ["", "", center(t, "[" + bar + "]", width), ""]
        lines.append(center(t, f"Round {min(self.round + 1, ROUNDS)}/{ROUNDS}    "
                               f"Hits: {self.hits} (need {NEEDED})", width))
        lines.append("")
        if self.phase == "playing":
            lines.append(center(t, t.bold("Press SPACE when the marker is in the green!"), width))
        elif self.phase == "pause":
            lines.append(center(t, "Nice!" if self.last_hit else "Missed!", width))
        else:
            won = self.hits >= NEEDED
            lines.append(center(t, t.bold_green("SUCCESS") if won else t.bold_red("FAILED"), width))
            lines.append(center(t, "[ENTER] continue", width))
        return lines
