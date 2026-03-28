import yaml
from pathlib import Path
from typing import Any, Dict


CONFIG_PATH = Path("config/sites.yaml")


def load_sites_config() -> Dict[str, Any]:
    """
    Load site configuration from YAML file.
    """
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)