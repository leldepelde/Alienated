
import sys
import traceback

from blessed import Terminal

from game.engine import Game
from game.scenes.minigame_dance import DanceScene


def main() -> int:
    term = Terminal()
    game = Game(term)
    game.push(DanceScene(game))
    try:
        with term.fullscreen(), term.cbreak(), term.hidden_cursor():
            game.run()
    except KeyboardInterrupt:
        pass
    except Exception:
        with open("crash.log", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        print("Oops - the game crashed. Details were saved to crash.log")
        return 1
    print("Thanks for playing!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
