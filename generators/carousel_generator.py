from pathlib import Path
from brand.prompt_builder import construir_prompt_carrusel
from generators.image_generator import generar_imagen, guardar_imagen


def generar_carrusel(titulo, puntos, marca, ruta_salida=None, slides=5):
    if len(puntos) < slides - 2:
        slides = len(puntos) + 2

    prompts = construir_prompt_carrusel(titulo, puntos, marca, slides)

    if ruta_salida is None:
        from ..config import ensure_output_dir
        ruta_salida = ensure_output_dir() / "carruseles"
    else:
        ruta_salida = Path(ruta_salida)

    ruta_salida.mkdir(parents=True, exist_ok=True)

    imagenes_generadas = []
    for info in prompts:
        num_slide = info["slide"]
        tipo = info["tipo"]
        prompt = info["prompt"]

        print(f"  Slide {num_slide}/{slides} ({tipo})...")
        img = generar_imagen(prompt, ancho=1080, alto=1350)

        nombre_archivo = f"slide_{num_slide:02d}_{tipo}.png"
        ruta_archivo = ruta_salida / nombre_archivo
        guardar_imagen(img, ruta_archivo)
        imagenes_generadas.append(ruta_archivo)
        print(f"  Guardado: {ruta_archivo}")

    return imagenes_generadas
