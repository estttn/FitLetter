from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_profile() -> dict:
    json_path = ROOT / "profile.json"
    if json_path.exists():
        with open(json_path, encoding="utf-8") as f:
            return json.load(f)
    yaml_path = ROOT / "profile.yaml"
    if yaml_path.exists():
        import yaml

        with open(yaml_path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    raise FileNotFoundError("profile.json or profile.yaml required")
