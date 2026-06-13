from dataclasses import dataclass

from src.config import TILE_SIZE


@dataclass
class PlayerData:
    name: str
    gender: str
    x: int = 19*TILE_SIZE
    y: int = 23*TILE_SIZE
    direction: str = "down"
    dormitory: str = ""
    easter_egg_found: bool = False  # 新增：彩蛋触发状态

    def to_dict(self):
        return {
            "name": self.name,
            "gender": self.gender,
            "x": self.x,
            "y": self.y,
            "direction": self.direction,
            "dormitory": self.dormitory, # 新字段
            "easter_egg_found": self.easter_egg_found  # 新字段
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get("name", ""),
            gender=data.get("gender", "男"),
            x=data.get("x", TILE_SIZE),
            y=data.get("y", TILE_SIZE),
            direction=data.get("direction", "down"),
            dormitory = data.get("dormitory", ""), # 新字段
            easter_egg_found = data.get("easter_egg_found", False)  # 读取新字段
        )
