import json
import os
from datetime import datetime

from src.player_data import PlayerData


class SaveManager:
    SLOT_COUNT = 3

    def __init__(self, save_dir="saves"):
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)

    def get_path(self, slot):
        return os.path.join(self.save_dir, f"save_{slot}.json")

    def has_save(self, slot):
        return os.path.exists(self.get_path(slot))

    def list_slots(self):
        return [self.load(slot) if self.has_save(slot) else None for slot in range(1, self.SLOT_COUNT + 1)]

    def load(self, slot):
        with open(self.get_path(slot), "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, slot, player_data, scene_name, current_building=None):
        data = {
            "version": 1,
            "slot": slot,
            "saved_at": datetime.now().isoformat(timespec="seconds"),
            "scene": scene_name,
            "current_building": current_building,
            "player": player_data.to_dict(),
            "game_time": {
                "day": 1,
                "hour": 8,
                "minute": 0
            },
            "dialog_progress": {}
        }
        with open(self.get_path(slot), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return data

    def delete(self, slot):
        path = self.get_path(slot)
        if os.path.exists(path):
            os.remove(path)

    def player_from_save(self, save_data):
        return PlayerData.from_dict(save_data.get("player", {}))
