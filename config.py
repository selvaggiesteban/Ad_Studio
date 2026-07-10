import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent
_repo_root = BASE_DIR.parent.parent
load_dotenv(_repo_root / ".env")
load_dotenv(_repo_root / "core" / "free-claude-code" / ".env")
load_dotenv()

OUTPUT_DIR = BASE_DIR / "output"
FORMATS_DIR = BASE_DIR / "formats"
BRAND_DIR = BASE_DIR / "brand_manuals"
TEMPLATES_DIR = BASE_DIR / "templates"

NVIDIA_API_KEY = os.getenv("NVIDIA_NIM_API_KEY", os.getenv("NVIDIA_API_KEY", ""))
NVIDIA_BASE_URL = "https://ai.api.nvidia.com/v1/genai"

POLLINATIONS_BASE_URL = "https://image.pollinations.ai/prompt"

MONEY_PRINTER_TURBO_PATH = os.getenv("MONEY_PRINTER_TURBO_PATH", "")

MODELS = {
    "schnell": {
        "id": "black-forest-labs/flux.1-schnell",
        "name": "FLUX.1 Schnell",
        "steps": 4,
        "speed": "rapido",
        "commercial": True,
    },
    "dev": {
        "id": "black-forest-labs/flux.1-dev",
        "name": "FLUX.1 Dev",
        "steps": 50,
        "speed": "lento",
        "commercial": False,
    },
    "kontext": {
        "id": "black-forest-labs/flux.1-kontext-dev",
        "name": "FLUX.1 Kontext",
        "steps": 50,
        "speed": "lento",
        "commercial": False,
    },
}

DEFAULT_MODEL = "schnell"

RESOLUTIONES_VALIDAS = [
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
            "NVIDIA_API_KEY no encontrado. "
            "Configuralo en .env o como variable de entorno."
        )
    return NVIDIA_API_KEY


def get_format_path(formato):
    path = FORMATS_DIR / f"{formato}.json"
    if not path.exists():
        raise FileNotFoundError(f"Formato no encontrado: {formato}")
    return path


def ensure_output_dir():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR
