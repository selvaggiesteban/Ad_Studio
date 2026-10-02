import json
from pathlib import Path


REQUIRED_FIELDS = ["nombre", "colores", "tono", "estilo"]
OPTIONAL_FIELDS = ["tipografia", "logo", "prohibido", "descripcion", "website", "redes"]


def cargar_brand_manual(path):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Brand manual not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        brand = json.load(f)

    errors = []
    for field in REQUIRED_FIELDS:
        if field not in brand:
            errors.append(f"Missing required field: {field}")

    if "colores" in brand:
        for color_key in ["primario", "secundario"]:
            if color_key not in brand["colores"]:
                errors.append(f"Missing color '{color_key}' in colors section")

    if errors:
        raise ValueError(f"Invalid brand manual:\n" + "\n".join(f"  - {e}" for e in errors))

    defaults = {
        "tipografia": {"titulares": "Arial Bold", "cuerpo": "Arial"},
        "logo": None,
        "prohibido": [],
        "descripcion": "",
        "website": "",
        "redes": {},
    }
    for key, val in defaults.items():
        if key not in brand:
            brand[key] = val

    return brand


def crear_brand_manual_ejemplo():
    return {
        "nombre": "Pizzeria Don Carlos",
        "descripcion": "Artisanal Italian pizzeria founded in 1985",
        "colores": {
            "primario": "#C41E3A",
            "secundario": "#FFD700",
            "acento": "#2E8B57",
            "fondo": "#FFFFFF",
            "texto": "#1A1A1A",
        },
        "tipografia": {
            "titulares": "Bebas Neue",
            "cuerpo": "Open Sans",
        },
        "logo": None,
        "tono": "casual, cordial, friendly",
        "estilo": "real food photos, vibrant colors, rustic Italian style",
        "prohibido": [
            "generic texts",
            "neon colors",
            "stock photos of smiling people",
        ],
        "website": "https://example-pizzeria.com",
        "redes": {
            "instagram": "@pizzeriadoncarlos",
            "facebook": "Pizzeria Don Carlos",
        },
    }


def guardar_brand_manual(brand, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(brand, f, indent=2, ensure_ascii=False)
    return path
