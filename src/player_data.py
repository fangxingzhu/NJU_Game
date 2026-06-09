from dataclasses import dataclass

from src.config import TILE_SIZE


@dataclass
class PlayerData:
    name: str
    gender: str
    x: int = 19*TILE_SIZE
    y: int = 23*TILE_SIZE
    direction: str = "down"

    def to_dict(self):
        return {
            "name": self.name,
            "gender": self.gender,
            "x": self.x,
            "y": self.y,
            "direction": self.direction
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get("name", ""),
            gender=data.get("gender", "男"),
            x=data.get("x", TILE_SIZE),
            y=data.get("y", TILE_SIZE),
            direction=data.get("direction", "down")
        )
