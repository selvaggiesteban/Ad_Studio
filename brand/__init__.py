import json
from pathlib import Path
from config import FORMATS_DIR

def cargar_formato(name):
    path = FORMATS_DIR / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"Format not found: {name}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def listar_formatos():
    formats = []
    for file in sorted(FORMATS_DIR.glob("*.json")):
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            formats.append({
                "nombre": file.stem,
                "descripcion": data.get("descripcion", ""),
                "ancho": data["ancho"],
                "alto": data["alto"],
                "plataformas": data.get("plataformas", []),
            })
    return formats
