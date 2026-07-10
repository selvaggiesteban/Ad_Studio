import json
from pathlib import Path


def cargar_formato(nombre):
    ruta = Path(__file__).parent.parent / "formats" / f"{nombre}.json"
    if not ruta.exists():
        raise FileNotFoundError(f"Formato no encontrado: {nombre}")
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def listar_formatos():
    formats_dir = Path(__file__).parent.parent / "formats"
    formatos = []
    for archivo in sorted(formats_dir.glob("*.json")):
        with open(archivo, "r", encoding="utf-8") as f:
            datos = json.load(f)
            formatos.append({
                "nombre": archivo.stem,
                "descripcion": datos.get("descripcion", ""),
                "ancho": datos["ancho"],
                "alto": datos["alto"],
                "plataformas": datos.get("plataformas", []),
            })
    return formatos
