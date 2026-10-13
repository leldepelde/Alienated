class Scene:

    def __init__(self, game):
        self.game = game
        self.term = game.term

    def handle_key(self, key: str):
        """Called once per keypress"""

    def update(self, dt: float):
        """Called every frame"""

    def draw(self, width: int, height: int) -> list:
        """Return the screen as a list of strings."""
        return []
