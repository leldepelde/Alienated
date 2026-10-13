
import time

from .constants import FPS, MIN_HEIGHT, MIN_WIDTH
from .input import normalize
from .state import GameState


class Game:
    def __init__(self, term):
        self.term = term
        self.state = GameState()
        self.scenes = []
        self.running = True
        self._needs_clear = True
        self._last_size = (0, 0)

    # ---- scene stack -------------------------------------------------------
    def push(self, scene):
        self.scenes.append(scene)
        self._needs_clear = True

    def pop(self):
        if self.scenes:
            self.scenes.pop()
            self._needs_clear = True

    def replace(self, scene):
        self.pop()
        self.push(scene)

    def quit(self):
        self.running = False

    # ---- main loop ---------------------------------------------------------
    def run(self):
        last = time.perf_counter()
        while self.running and self.scenes:
            key = self.term.inkey(timeout=1 / FPS)   # waits up to 1/20 s for a key
            now = time.perf_counter()
            dt = min(now - last, 0.25)               # seconds since last frame
            last = now

            if key:
                self.scenes[-1].handle_key(normalize(key))
            if not (self.running and self.scenes):
                break
            self.scenes[-1].update(dt)
            if not (self.running and self.scenes):
                break
            self.render()

    def render(self):
        t = self.term
        w, h = t.width, t.height
        if (w, h) != self._last_size:
            self._last_size = (w, h)
            self._needs_clear = True

        if w < MIN_WIDTH or h < MIN_HEIGHT:
            lines = ["", f" Terminal too small ({w}x{h}).",
                     f" Please resize to at least {MIN_WIDTH}x{MIN_HEIGHT}."]
        else:
            lines = self.scenes[-1].draw(w, h)

        out = []
        if self._needs_clear:
            out.append(t.clear)
            self._needs_clear = False
        for y, line in enumerate(lines[: h - 1]):
            out.append(t.move_xy(0, y) + line + t.clear_eol)
        out.append(t.move_xy(0, min(len(lines), h - 1)) + t.clear_eos)
        print("".join(out), end="", flush=True)
