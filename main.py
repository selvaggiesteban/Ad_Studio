#!/usr/bin/env python3
"""
ad_studio - Generador de contenido visual para redes sociales
CLI en español que genera imágenes y videos usando IA.
"""

import argparse
import json
import sys
from pathlib import Path

from config import OUTPUT_DIR, BRAND_DIR, FORMATS_DIR
from brand.loader import cargar_brand_manual, crear_brand_manual_ejemplo, guardar_brand_manual
from brand.prompt_builder import construir_prompt
from brand import cargar_formato, listar_formatos
from generators.image_generator import generar_imagen, guardar_imagen, verificar_motores
from generators.carousel_generator import generar_carrusel
from generators.thumbnail_generator import generar_thumbnail
from generators.video_generator import generar_video, verificar_money_printer_turbo


def cmd_imagen(args):
    print(f"\n{'='*60}")
    print(f"  Generando imagen: {args.tipo}")
    print(f"{'='*60}\n")

    marca = None
    if args.marca:
        print(f"Cargando brand manual: {args.marca}")
        marca = cargar_brand_manual(args.marca)
        print(f"  Marca: {marca['nombre']}\n")

    formato = None
    try:
        formato = cargar_formato(args.tipo)
        print(f"Formato: {formato['nombre']} ({formato['ancho']}x{formato['alto']})\n")
    except FileNotFoundError:
        print(f"Formato '{args.tipo}' no encontrado, usando 1024x1024 por defecto\n")
        formato = {"ancho": 1024, "alto": 1024}

    if marca:
        prompt = construir_prompt(args.prompt, marca, formato)
    else:
        prompt = args.prompt

    print(f"Prompt: {prompt[:200]}...\n" if len(prompt) > 200 else f"Prompt: {prompt}\n")

    img = generar_imagen(
        prompt,
        ancho=formato["ancho"],
        alto=formato["alto"],
        modelo=args.modelo,
    )

    nombre_limpio = args.prompt.lower().replace(" ", "_")[:50]
    nombre_archivo = f"{args.tipo}_{nombre_limpio}.png"
    ruta = OUTPUT_DIR / nombre_archivo
    guardar_imagen(img, ruta)

    print(f"\nImagen guardada: {ruta}")
    return ruta


def cmd_carrusel(args):
    print(f"\n{'='*60}")
    print(f"  Generando carrusel: {args.titulo}")
    print(f"{'='*60}\n")

    marca = None
    if args.marca:
        print(f"Cargando brand manual: {args.marca}")
        marca = cargar_brand_manual(args.marca)
        print(f"  Marca: {marca['nombre']}\n")

    if not marca:
        marca = crear_brand_manual_ejemplo()
        print("Usando brand manual de ejemplo\n")

    puntos = args.puntos if args.puntos else [f"Punto {i+1}" for i in range(args.slides - 2)]

    ruta_salida = OUTPUT_DIR / "carruseles"
    imagenes = generar_carrusel(args.titulo, puntos, marca, ruta_salida, args.slides)

    print(f"\nCarrusel generado: {len(imagenes)} slides en {ruta_salida}")
    return imagenes


def cmd_thumbnail(args):
    print(f"\n{'='*60}")
    print(f"  Generando miniatura YouTube")
    print(f"{'='*60}\n")

    marca = None
    if args.marca:
        print(f"Cargando brand manual: {args.marca}")
        marca = cargar_brand_manual(args.marca)
        print(f"  Marca: {marca['nombre']}\n")

    if not marca:
        marca = crear_brand_manual_ejemplo()
        print("Usando brand manual de ejemplo\n")

    ruta = generar_thumbnail(args.titulo, marca, args.tono)

    print(f"\nMiniatura guardada: {ruta}")
    return ruta


def cmd_video(args):
    print(f"\n{'='*60}")
    print(f"  Generando video: {args.prompt}")
    print(f"{'='*60}\n")

    marca = None
    if args.marca:
        print(f"Cargando brand manual: {args.marca}")
        marca = cargar_brand_manual(args.marca)
        print(f"  Marca: {marca['nombre']}\n")

    video_path = generar_video(
        args.prompt,
        duracion=args.duracion,
        aspecto=args.aspecto,
        idioma=args.idioma,
        marca=marca,
    )

    if video_path:
        print(f"\nVideo guardado: {video_path}")
    else:
        print("\nVideo generado pero no se encontro el archivo de salida")

    return video_path


def cmd_lote(args):
    print(f"\n{'='*60}")
    print(f"  Generando lote desde: {args.archivo}")
    print(f"{'='*60}\n")

    with open(args.archivo, "r", encoding="utf-8") as f:
        posts = json.load(f)

    marca = None
    if args.marca:
        print(f"Cargando brand manual: {args.marca}")
        marca = cargar_brand_manual(args.marca)
        print(f"  Marca: {marca['nombre']}\n")

    resultados = []
    for i, post in enumerate(posts, 1):
        print(f"\n--- Post {i}/{len(posts)} ---")
        tipo = post.get("tipo", "instagram_post")
        prompt = post.get("prompt", "")

        try:
            formato = cargar_formato(tipo)
        except FileNotFoundError:
            formato = {"ancho": 1024, "alto": 1024}

        if marca:
            prompt_completo = construir_prompt(prompt, marca, formato)
        else:
            prompt_completo = prompt

        img = generar_imagen(prompt_completo, ancho=formato["ancho"], alto=formato["alto"])

        nombre_limpio = prompt.lower().replace(" ", "_")[:50]
        nombre_archivo = f"{tipo}_{i:03d}_{nombre_limpio}.png"
        ruta = OUTPUT_DIR / nombre_archivo
        guardar_imagen(img, ruta)
        resultados.append(str(ruta))
        print(f"  Guardado: {ruta}")

    print(f"\nLote completado: {len(resultados)} imagenes generadas")
    return resultados


def cmd_formatos(args):
    formatos = listar_formatos()
    print(f"\n{'='*60}")
    print(f"  Formatos disponibles ({len(formatos)})")
    print(f"{'='*60}\n")

    for fmt in formatos:
        plataformas = ", ".join(fmt["plataformas"])
        print(f"  {fmt['nombre']:<25} {fmt['ancho']:>5}x{fmt['alto']:<5}  [{plataformas}]")

    print()
    return formatos


def cmd_verificar(args):
    print(f"\n{'='*60}")
    print(f"  Verificando motores de generacion")
    print(f"{'='*60}\n")

    resultados = verificar_motores()

    for motor, info in resultados.items():
        status = info["status"]
        simbolo = "OK" if status == "ok" else "FALLO"
        print(f"  [{simbolo}] {motor}: {info.get('mensaje', status)}")

    estado_mpt = verificar_money_printer_turbo()
    simbolo = "OK" if estado_mpt["status"] == "ok" else "INFO"
    print(f"  [{simbolo}] money_printer_turbo: {estado_mpt['mensaje']}")

    print()
    return resultados


def cmd_marca(args):
    if args.crear:
        print(f"\nCreando brand manual: {args.crear}")
        marca = crear_brand_manual_ejemplo()
        marca["nombre"] = args.crear
        ruta = BRAND_DIR / f"{args.crear.lower().replace(' ', '_')}.json"
        guardar_brand_manual(marca, ruta)
        print(f"Brand manual creado: {ruta}")
        print("Edita el archivo para personalizar colores, estilo, etc.")
        return ruta

    if args.listar:
        print(f"\nBrand manuals disponibles:")
        for archivo in sorted(BRAND_DIR.glob("*.json")):
            with open(archivo, "r", encoding="utf-8") as f:
                m = json.load(f)
            print(f"  {archivo.stem}: {m.get('nombre', 'Sin nombre')}")
        print()
        return

    print("\nUso:")
    print("  python main.py marca --crear 'NombreMarca'")
    print("  python main.py marca --listar")


def main():
    parser = argparse.ArgumentParser(
        prog="ad_studio",
        description="Generador de contenido visual para redes sociales",
    )
    subparsers = parser.add_subparsers(dest="comando", help="Comandos disponibles")

    p_imagen = subparsers.add_parser("imagen", help="Generar imagen para una red social")
    p_imagen.add_argument("--tipo", required=True, help="Tipo de formato (ej: instagram_post)")
    p_imagen.add_argument("--prompt", required=True, help="Descripcion de la imagen")
    p_imagen.add_argument("--marca", help="Ruta al brand manual JSON")
    p_imagen.add_argument("--modelo", default="schnell", choices=["schnell", "dev", "kontext"])
    p_imagen.set_defaults(func=cmd_imagen)

    p_carrusel = subparsers.add_parser("carrusel", help="Generar carrusel slide-by-slide")
    p_carrusel.add_argument("--titulo", required=True, help="Titulo del carrusel")
    p_carrusel.add_argument("--puntos", nargs="+", help="Puntos/ideas por slide")
    p_carrusel.add_argument("--slides", type=int, default=5, help="Numero de slides (default: 5)")
    p_carrusel.add_argument("--marca", help="Ruta al brand manual JSON")
    p_carrusel.set_defaults(func=cmd_carrusel)

    p_thumb = subparsers.add_parser("thumbnail", help="Generar miniatura YouTube")
    p_thumb.add_argument("--titulo", required=True, help="Titulo del video")
    p_thumb.add_argument("--marca", help="Ruta al brand manual JSON")
    p_thumb.add_argument("--tono", default="profesional",
                         choices=["profesional", "casual", "sorpresa", "curioso", "directo"])
    p_thumb.set_defaults(func=cmd_thumbnail)

    p_video = subparsers.add_parser("video", help="Generar video corto (MoneyPrinterTurbo)")
    p_video.add_argument("--prompt", required=True, help="Tema del video")
    p_video.add_argument("--duracion", type=int, default=15, help="Duracion en segundos")
    p_video.add_argument("--aspecto", default="9:16", choices=["9:16", "16:9"])
    p_video.add_argument("--idioma", default="es", help="Idioma del script")
    p_video.add_argument("--marca", help="Ruta al brand manual JSON")
    p_video.set_defaults(func=cmd_video)

    p_lote = subparsers.add_parser("lote", help="Generar batch de imagenes desde JSON")
    p_lote.add_argument("--archivo", required=True, help="Ruta al archivo JSON con posts")
    p_lote.add_argument("--marca", help="Ruta al brand manual JSON")
    p_lote.set_defaults(func=cmd_lote)

    p_formatos = subparsers.add_parser("formatos", help="Listar formatos disponibles")
    p_formatos.set_defaults(func=cmd_formatos)

    p_verificar = subparsers.add_parser("verificar", help="Verificar motores disponibles")
    p_verificar.set_defaults(func=cmd_verificar)

    p_marca = subparsers.add_parser("marca", help="Gestionar brand manuals")
    p_marca.add_argument("--crear", help="Crear nuevo brand manual con nombre")
    p_marca.add_argument("--listar", action="store_true", help="Listar brand manuals")
    p_marca.set_defaults(func=cmd_marca)

    args = parser.parse_args()

    if not args.comando:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
