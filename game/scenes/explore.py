from ..input import CONFIRM_KEYS, MOVES
from ..ui import center
from ..world import INTERACTABLES, SHIP_MAP, WALKABLE
from .base import Scene
from ..story.dialogues import DIALOGUES
from .dialogue import DialogueScene
from .minigame_dance import DanceScene
from .note import NoteScene
from .paywall import PaywallScene
from ..art.items import NOTE_SCRAP
from .minigame_timing import TimingMinigame
from .minigame_decode import SignalDecodeMinigame


class ExploreScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.grid = [list(row) for row in SHIP_MAP]
        self.px = self.py = 1
        for y, row in enumerate(self.grid):
            for x, ch in enumerate(row):
                if ch == "@":
                    self.px, self.py = x, y
                    self.grid[y][x] = "."
        self.message = ""
        self.message_timer = 0.0
        self.lock = 0.0

    # -- input -------------------------------
    def handle_key(self, key):
        if key in MOVES:
            dx, dy = MOVES[key]
            nx, ny = self.px + dx, self.py + dy
            if self.tile(nx, ny) in WALKABLE:      # walls and objects block you
                self.px, self.py = nx, ny
        elif key in CONFIRM_KEYS and self.lock <= 0:
            near = self.nearby()
            if near:
                self.interact(near[1])
        elif key == "esc":
            self.game.quit()

    def update(self, dt):
        if self.lock > 0:
            self.lock -= dt
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = ""

    # ---- helpers -----------------------------------------------------------
    def tile(self, x, y):
        if 0 <= y < len(self.grid) and 0 <= x < len(self.grid[y]):
            return self.grid[y][x]
        return "#"

    def nearby(self):
        """Return (char, interactable_dict) for something next to the player."""
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            ch = self.tile(self.px + dx, self.py + dy)
            if ch in INTERACTABLES:
                return ch, INTERACTABLES[ch]
        return None

    def say(self, text, seconds=3.0):
        self.message, self.message_timer = text, seconds

    def interact(self, thing):
        if thing["kind"] == "talk":
            who = thing["target"]
            intro = f"{who}_intro"
            invasion = f"{who}_invasion_signal"
            flags = self.game.state.flags
            after = f"{who}_after_console"       # one-time reaction
            if intro not in flags:
                script = intro
            elif after in DIALOGUES and after not in flags and flags & {"console_fixed", "console_failed"}:
                script = after
            elif invasion in DIALOGUES and invasion not in flags and flags & {"signal_decoded", "signal_failed"}:
                script = invasion
            else:
                script = f"{who}_chat"
            on_done = self.start_dance if script == invasion else None
            self.game.push(DialogueScene(self.game, script, on_done=on_done))
        elif thing["kind"] == "minigame":
            self.game.push(TimingMinigame(
                self.game, helper_id=thing["target"], title="ENGINE CONSOLE",
                on_done=self.after_minigame))
        elif thing["kind"] == "note":
            self.game.push(NoteScene(
            self.game, NOTE_SCRAP,
            caption="A torn scrap of paper, covered in alien writing."))
        elif thing["kind"] == "decode":
            if "console_fixed" not in self.game.state.flags:
                self.say("Static. The comms array needs power first.")
                return
            self.game.push(SignalDecodeMinigame(
                self.game, helper_id=thing["target"], on_done=self.after_decode))

    def after_minigame(self, success):
            self.lock = 0.5
            flags = self.game.state.flags
            flags.discard("console_fixed")
            flags.discard("console_failed")
            flags.add("console_fixed" if success else "console_failed")
            self.say("The console hums back to life." if success else "The console sparks. Not good...")
    def start_dance(self):
    # only dance if the signal was decoded
        if "signal_decoded" in self.game.state.flags:
            self.game.push(DanceScene(self.game, on_done=self.after_dance))
    def after_dance(self, success):
        self.lock = 0.5
        flags = self.game.state.flags
        flags.discard("danced")
        flags.discard("dance_failed")
        flags.add("danced" if success else "dance_failed")
        self.say("The alien is delighted!" if success else "The alien looks confused...")
        self.game.push(PaywallScene(self.game))      # end of the gam

    def after_decode(self, success):
            flags = self.game.state.flags
            flags.discard("signal_decoded")
            flags.discard("signal_failed")
            flags.add("signal_decoded" if success else "signal_failed")
            self.say("The message resolves into words you understand." if success
             else "The signal dissolves back into static. You'll have to try again.")

    # ---- drawing -------------------
    def style(self, ch):
        t = self.term
        if ch == "#":
            return t.white("#")
        if ch == ".":
            return t.color(8)(".")
        if ch == "V":
            return t.bold_magenta("V")
        if ch == "R":
            return t.bold_cyan("R")
        if ch == "E":
            return t.bold_green("E")
        if ch == "N":
            return t.bold_white("N")
        if ch == "C":
            return t.bold_red("E")
        return ch

    def draw(self, width, height):
        t = self.term
        lines = [center(t, t.bold("ALIENATED - heading for Mars"), width), ""]
        for y, row in enumerate(self.grid):
            s = ""
            for x, ch in enumerate(row):
                s += t.bold_yellow("@") if (x, y) == (self.px, self.py) else self.style(ch)
            lines.append(center(t, s, width))
        lines.append("")
        near = self.nearby()
        if near:
            lines.append(center(t, t.bold(f"[E] {near[1]['label']}"), width))
        else:
            lines.append("")
        lines.append(center(t, self.message, width))
        return lines