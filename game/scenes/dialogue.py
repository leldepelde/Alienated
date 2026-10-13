
from ..art.portraits import get_portrait
from ..characters import CHARACTERS
from ..input import CONFIRM_KEYS
from ..story.dialogues import DIALOGUES
from ..ui import box, center, color, wrap
from .base import Scene

CHARS_PER_SECOND = 45     # typewriter speed
BOX_WIDTH = 60
PORTRAIT_ROWS = 28


class DialogueScene(Scene):
    def __init__(self, game, script_id, on_done=None):
        super().__init__(game)
        self.script_id = script_id
        self.script = DIALOGUES[script_id]
        self.on_done = on_done
        self.node = None
        self.elapsed = 0.0
        self.choice = 0
        self.feedback = ""
        self.feedback_timer = 0.0
        self.enter_node("start")

    # ---- story flow -------------------------
    def enter_node(self, node_id):
        self.node = self.script[node_id]
        self.elapsed = 0.0
        self.choice = 0
        self.apply_affect(self.node.get("affect"))
        for flag in self.node.get("set_flags", []):
            self.game.state.flags.add(flag)

    def apply_affect(self, affect):
        for char_id, delta in (affect or {}).items():
            self.game.state.change_rel(char_id, delta)
            name = CHARACTERS[char_id].name
            self.feedback = f"{name} {'+' if delta > 0 else ''}{delta}"
            self.feedback_timer = 2.0

    def finish(self):
        self.game.state.flags.add(self.script_id)   # remember we've had this talk
        self.game.pop()
        if self.on_done:
            self.on_done()

    def typing(self):
        return int(self.elapsed * CHARS_PER_SECOND) < len(self.node["text"])

    def advance(self):
        choices = self.node.get("choices")
        if choices:
            picked = choices[self.choice]
            self.apply_affect(picked.get("affect"))
            self.enter_node(picked["goto"])
            return
        nxt = self.node.get("next")
        if callable(nxt):
            nxt = nxt(self.game.state)
        if nxt:
            self.enter_node(nxt)
        else:
            self.finish()

    # ---- input / update ------
    def handle_key(self, key):
        if self.typing():
            if key in CONFIRM_KEYS:
                self.elapsed = 9999      # skip typewriter, show full line
            return
        choices = self.node.get("choices")
        if choices:
            if key in ("up", "w"):
                self.choice = (self.choice - 1) % len(choices)
            elif key in ("down", "s"):
                self.choice = (self.choice + 1) % len(choices)
            elif key.isdigit() and 1 <= int(key) <= len(choices):
                self.choice = int(key) - 1
                self.advance()
            elif key in CONFIRM_KEYS:
                self.advance()
        elif key in CONFIRM_KEYS:
            self.advance()

    def update(self, dt):
        self.elapsed += dt
        if self.feedback_timer > 0:
            self.feedback_timer -= dt

    # ---- drawing ---
    def draw(self, width, height):
        t = self.term
        speaker = self.node.get("speaker", "narrator")
        char = CHARACTERS.get(speaker)
        portrait = get_portrait(speaker, self.node.get("mood", "neutral"))

        lines = []
        # portrait area is always 10 rows tall so the text box doesn't jump around
        art_rows = [center(t, color(t, char.color if char else "white", row), width)
                    for row in portrait]
        art_rows += [""] * (PORTRAIT_ROWS - len(art_rows))
        lines += art_rows[:PORTRAIT_ROWS]
        lines.append(center(t, t.bold_yellow(self.feedback) if self.feedback_timer > 0 else "", width))

        shown = self.node["text"][: int(self.elapsed * CHARS_PER_SECOND)]
        body = wrap(shown, BOX_WIDTH - 4)
        body += [""] * (4 - len(body))
        title = f"{char.name} - {char.role}" if char else ""
        text_box = box(t, body, BOX_WIDTH, title)
        lines += [center(t, row, width) for row in text_box]

        lines.append("")
        if not self.typing():
            choices = self.node.get("choices")
            if choices:
                for i, c in enumerate(choices):
                    label = f"{i + 1}. {c['text']}"
                    row = t.bold_black_on_white(f" {label} ") if i == self.choice else f" {label} "
                    lines.append(center(t, row, width))
            else:
                lines.append(center(t, "[ENTER] continue", width))
        return lines
