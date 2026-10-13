from ..ui import center
from .base import Scene
from .explore import ExploreScene

#  (patorjk.com/software/taag generates ASCII lettering)
LOGO = r"""
   ▄████████  ▄█        ▄█     ▄████████ ███▄▄▄▄      ▄████████     ███        ▄████████ ████████▄  
  ███    ███ ███       ███    ███    ███ ███▀▀▀██▄   ███    ███ ▀█████████▄   ███    ███ ███   ▀███ 
  ███    ███ ███       ███▌   ███    █▀  ███   ███   ███    ███    ▀███▀▀██   ███    █▀  ███    ███ 
  ███    ███ ███       ███▌  ▄███▄▄▄     ███   ███   ███    ███     ███   ▀  ▄███▄▄▄     ███    ███ 
▀███████████ ███       ███▌ ▀▀███▀▀▀     ███   ███ ▀███████████     ███     ▀▀███▀▀▀     ███    ███ 
  ███    ███ ███       ███    ███    █▄  ███   ███   ███    ███     ███       ███    █▄  ███    ███ 
  ███    ███ ███▌    ▄ ███    ███    ███ ███   ███   ███    ███     ███       ███    ███ ███   ▄███ 
  ███    █▀  █████▄▄██ █▀     ██████████  ▀█   █▀    ███    █▀     ▄████▀     ██████████ ████████▀  
             ▀                                                                                      
  """.strip("\n").splitlines()


class TitleScene(Scene):
    def draw(self, width, height):
        t = self.term
        lines = [""] * 5
        lines += [center(t, t.bold_red(row), width) for row in LOGO]
        lines += ["", center(t, "A game about the end of the world", width), ""]
        lines += [center(t, t.bold("Press ENTER to start"), width)]
        lines += ["", center(t, "Move: arrows / WASD    Interact: E    Quit: ESC", width)]
        return lines

    def handle_key(self, key):
        if key == "enter":
            self.game.replace(ExploreScene(self.game))
        elif key == "esc":
            self.game.quit()
