from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AIConfig:
    """Configuration for the AI player."""

    elo: int = 1400
    think_time_ms: int = 1000


@dataclass
class Config:
    """Application configuration."""

    stockfish_path: str | None = None
    ai: AIConfig | None = None

    def __post_init__(self):
        if self.ai is None:
            self.ai = AIConfig()


def load_config(config_path: str | Path | None = None) -> Config:
    """
    Load configuration from a JSON file.

    Args:
        config_path: Path to config file. Defaults to config.json in project root.

    Returns:
        Config object with loaded values or defaults.
    """
    if config_path is None:
        config_path = Path(__file__).parent.parent / "config.json"
    else:
        config_path = Path(config_path)

    if not config_path.exists():
        return Config()

    with open(config_path, "r") as f:
        data = json.load(f)

    ai_data = data.get("ai", {})
    ai_config = AIConfig(
        elo=ai_data.get("elo", 1400),
        think_time_ms=ai_data.get("think_time_ms", 1000),
    )

    return Config(
        stockfish_path=data.get("stockfish_path"),
        ai=ai_config,
    )
