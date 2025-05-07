import os
from pathlib import Path

OI_CLI_API_KEY = os.getenv("OI_CLI_API_KEY")
OI_CLI_DIR = Path(os.getenv("OI_CLI_DIR", Path.home() / ".oi_cli"))
OI_CLI_DIR.mkdir(parents=True, exist_ok=True)
