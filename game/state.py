from dataclasses import dataclass, field

from .characters import CHARACTERS


@dataclass
class GameState:
    relationships: dict = field(
        default_factory=lambda: {c.id: c.start_relationship for c in CHARACTERS.values()}
    )
    flags: set = field(default_factory=set)   # story flags, e.g. "vera_intro"

    def rel(self, char_id: str) -> int:
        return self.relationships.get(char_id, 0)

    def change_rel(self, char_id: str, delta: int) -> int:
        new = max(0, min(100, self.rel(char_id) + delta))
        self.relationships[char_id] = new
        return new

    def assist(self, char_id: str) -> float:
        """0.0 (they barely help) .. 1.0 (best friends). Minigames use this to
        scale their difficulty - this is the 'better relationship = easier' rule."""
        return self.rel(char_id) / 100
