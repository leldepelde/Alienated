from ..ui import center
from .base import Scene


class NoteScene(Scene):
    def __init__(self, game, art: list, caption: str = ""):
        super().__init__(game)
        self.art = art
        self.caption = caption

    def handle_key(self, key):
        self.game.pop()   # any key closes it

    def draw(self, width, height):
        t = self.term
        lines = [center(t, t.bold_white(row), width) for row in self.art]
        if self.caption:
            lines.append(center(t, self.caption, width))
        lines.append(center(t, "[any key] close", width))
        return lines
