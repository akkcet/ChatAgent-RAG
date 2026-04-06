import json
import os
from pathlib import Path

class OrderManager:
    def __init__(self):
        self.order_file = Path(__file__).parent / "data" / "orders.json"
        if not self.order_file.exists():
            with open(self.order_file, "w") as f:
                json.dump({}, f)

    def save_order(self, user_id, items):
        data = self._load()
        data.setdefault(user_id, [])
        data[user_id].append(items)
        self._save(data)

    def get_order_history(self, user_id):
        data = self._load()
        return data.get(user_id, [])

    def _load(self):
        with open(self.order_file, "r") as f:
            return json.load(f)

    def _save(self, data):
        with open(self.order_file, "w") as f:
            json.dump(data, f, indent=2)