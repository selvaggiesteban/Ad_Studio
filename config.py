import os
from pathlib import Path
from dotenv import load_dotenv

# Use absolute path relative to this file for total OS agnosticism
BASE_DIR = Path(__file__).parent.absolute()
load_dotenv(BASE_DIR / ".env")
load_dotenv()

# Output and Asset directories
OUTPUT_DIR = BASE_DIR / "output"
FORMATS_DIR = BASE_DIR / "formats"
BRAND_DIR = BASE_DIR / "brand_manuals"
TEMPLATES_DIR = BASE_DIR / "templates"

# API Configuration
NVIDIA_API_KEY = os.getenv("NVIDIA_NIM_API_KEY", os.getenv("NVIDIA_API_KEY", ""))
NVIDIA_BASE_URL = "https://ai.api.nvidia.com/v1/genai"

POLLINATIONS_BASE_URL = "https://image.pollinations.ai/prompt"

# External Tools Path (Must be defined in .env)
MONEY_PRINTER_TURBO_PATH = os.getenv("MONEY_PRINTER_TURBO_PATH", "")

MODELS = {
    "schnell": {
        "id": "black-forest-labs/flux.1-schnell",
        "name": "FLUX.1 Schnell",
        "steps": 4,
        "speed": "fast",
        "commercial": True,
    },
    "dev": {
        "id": "black-forest-labs/flux.1-dev",
        "name": "FLUX.1 Dev",
        "steps": 50,
        "speed": "slow",
        "commercial": False,
    },
    "kontext": {
        "id": "black-forest-labs/flux.1-kontext-dev",
        "name": "FLUX.1 Kontext",
        "steps": 50,
        "speed": "slow",
        "commercial": False,
    },
}

DEFAULT_MODEL = "schnell"

VALID_RESOLUTIONS = [
    (1024, 1024),
    (768, 1344),
    (1344, 768),
    (832, 1216),
    (1216, 832),
    (896, 1152),
    (1152, 896),
]


def get_api_key():
    if not NVIDIA_API_KEY:
        raise ValueError(
            "NVIDIA_API_KEY not found. "
            "Please configure it in .env or as an environment variable."
        )
    return NVIDIA_API_KEY


def get_format_path(format_name):
    path = FORMATS_DIR / f"{format_name}.json"
    if not path.exists():
        raise FileNotFoundError(f"Format not found: {format_name}")
    return path


def ensure_output_dir():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR
