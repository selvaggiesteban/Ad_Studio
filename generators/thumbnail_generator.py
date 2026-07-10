from pathlib import Path
from brand.prompt_builder import construir_prompt_thumbnail
from generators.image_generator import generar_imagen, guardar_imagen


def generar_thumbnail(titulo, marca, tono="profesional", ruta_salida=None):
    prompt = construir_prompt_thumbnail(titulo, marca, tono)

    if ruta_salida is None:
        from ..config import ensure_output_dir
        ruta_salida = ensure_output_dir()
    else:
        ruta_salida = Path(ruta_salida)

    ruta_salida.mkdir(parents=True, exist_ok=True)

    nombre_limpio = titulo.lower().replace(" ", "_")[:50]
    nombre_archivo = f"thumbnail_{nombre_limpio}.png"
    ruta_archivo = ruta_salida / nombre_archivo

    print(f"  Generando miniatura: {titulo}")
    img = generar_imagen(prompt, ancho=1280, alto=720)
    guardar_imagen(img, ruta_archivo)
    print(f"  Guardado: {ruta_archivo}")

    return ruta_archivo
