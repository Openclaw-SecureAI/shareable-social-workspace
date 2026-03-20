from __future__ import annotations

import json
import os
from pathlib import Path


def detect_root() -> Path:
    override = os.environ.get("SOCIAL_WORKSPACE_ROOT")
    if override:
        return Path(override).expanduser().resolve()
    return Path(__file__).resolve().parent


ROOT = detect_root()
DRAFTS = ROOT / 'drafts'
CONFIG = ROOT / 'config'
STATE_DIRS = ['pending', 'approved', 'scheduled', 'published', 'rejected']


def load_json(path: Path):
    return json.loads(path.read_text())


def save_json(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + '\n')


def load_defaults():
    return load_json(CONFIG / 'defaults.json')
