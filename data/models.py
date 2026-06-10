import json
import os
from datetime import datetime
from typing import Dict, List, Optional

DATA_DIR = "data_storage"
os.makedirs(DATA_DIR, exist_ok=True)

class JSONStorage:
    @staticmethod
    def _get_path(name: str) -> str:
        return os.path.join(DATA_DIR, f"{name}.json")

    @classmethod
    def save(cls, name: str, data: List[Dict]) -> None:
        with open(cls._get_path(name), "w") as f:
            json.dump(data, f, indent=2, default=str)

    @classmethod
    def load(cls, name: str) -> List[Dict]:
        path = cls._get_path(name)
        if not os.path.exists(path):
            return []
        with open(path, "r") as f:
            return json.load(f)

    @classmethod
    def append(cls, name: str, item: Dict) -> None:
        data = cls.load(name)
        data.append(item)
        cls.save(name, data)

# Simple ORM-like classes
class Order:
    _storage = "orders"
    @classmethod
    def create(cls, **kwargs):
        kwargs["id"] = len(cls.all()) + 1
        kwargs["created_at"] = datetime.utcnow().isoformat()
        JSONStorage.append(cls._storage, kwargs)
        return kwargs

    @classmethod
    def all(cls):
        return JSONStorage.load(cls._storage)

class Position:
    _storage = "positions"
    @classmethod
    def create(cls, **kwargs):
        kwargs["updated_at"] = datetime.utcnow().isoformat()
        JSONStorage.append(cls._storage, kwargs)
        return kwargs

    @classmethod
    def all(cls):
        return JSONStorage.load(cls._storage)

class RiskSnapshot:
    _storage = "risk_snapshots"
    @classmethod
    def create(cls, **kwargs):
        kwargs["timestamp"] = datetime.utcnow().isoformat()
        JSONStorage.append(cls._storage, kwargs)
        return kwargs

    @classmethod
    def latest(cls):
        data = JSONStorage.load(cls._storage)
        return data[-1] if data else None

class Instrument:
    _storage = "instruments"
    @classmethod
    def get_or_create(cls, ticker: str) -> Dict:
        instruments = JSONStorage.load(cls._storage)
        for inst in instruments:
            if inst["ticker"] == ticker:
                return inst
        new = {"id": len(instruments)+1, "ticker": ticker, "asset_class": "equity"}
        JSONStorage.append(cls._storage, new)
        return new

# Re-export for compatibility
Base = None  # Not needed
