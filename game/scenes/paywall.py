from ..art.paywall import PAYWALL
from ..input import CONFIRM_KEYS
from ..ui import center
from .base import Scene

DECLINED = [
    "Payment declined. Aliens want real money. More. More. More.",
    "Payment declined again. Have you tried a bigger wallet? Or another card?",
    "Still declined. Humanity will end because you're broke.",
]


class PaywallScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.attempts = 0

    def handle_key(self, key):
        if key == "esc":
            self.game.quit()                 # the only way out
        elif key in CONFIRM_KEYS:
            self.attempts += 1               # "pay now" never works

    def draw(self, width, height):
        t = self.term
        lines = [center(t, t.bold_yellow(row), width) for row in PAYWALL]
        lines.append("")
        if self.attempts:
            msg = DECLINED[min(self.attempts, len(DECLINED)) - 1]
            lines.append(center(t, t.bold_red(msg), width))
        else:
            lines.append("")
        lines.append(center(t, "[ENTER] pay now!      [ESC] quit", width))
        return lines
