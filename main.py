#!/usr/bin/env python3
"""
ad_studio - Visual Content Generator for Social Media
English CLI that generates images and videos using AI.
"""

import argparse
import json
import sys
import logging
from pathlib import Path

from config import OUTPUT_DIR, BRAND_DIR, FORMATS_DIR, ensure_output_dir
from brand.loader import cargar_brand_manual, crear_brand_manual_ejemplo, guardar_brand_manual
from brand.prompt_builder import build_prompt, build_carousel_prompts, build_thumbnail_prompt
from brand import cargar_formato, listar_formatos
from generators.image_generator import generate_image, save_image, verify_engines
from generators.carousel_generator import generate_carousel
from generators.thumbnail_generator import generate_thumbnail
from generators.video_generator import generate_video, verify_money_printer_turbo

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger("ad_studio")

def cmd_image(args):
    logger.info(f"Generating image: {args.type}")

    brand = None
    if args.brand:
        logger.info(f"Loading brand manual: {args.brand}")
        brand = cargar_brand_manual(args.brand)
        logger.info(f"Brand: {brand['nombre']}")

    format_data = None
    try:
        format_data = cargar_formato(args.type)
        logger.info(f"Format: {format_data['nombre']} ({format_data['ancho']}x{format_data['alto']})")
    except FileNotFoundError:
        logger.warning(f"Format '{args.type}' not found, using 1024x1024 default")
        format_data = {"ancho": 1024, "alto": 1024}

    if brand:
        prompt = build_prompt(args.prompt, brand, format_data)
    else:
        prompt = args.prompt

    logger.info(f"Prompt: {prompt[:200]}..." if len(prompt) > 200 else f"Prompt: {prompt}")

    img = generate_image(
        prompt,
        width=format_data["ancho"],
        height=format_data["alto"],
        model=args.model,
    )

    # OS-Agnostic Pathing: Output subfolder by brand
    brand_name = brand['nombre'].lower().replace(" ", "_") if brand else "general"
    ensure_output_dir()
    final_output_dir = OUTPUT_DIR / brand_name
    final_output_dir.mkdir(parents=True, exist_ok=True)

    clean_name = args.prompt.lower().replace(" ", "_")[:50]
    filename = f"{args.type}_{clean_name}.png"
    path = final_output_dir / filename
    save_image(img, path)

    logger.info(f"Image saved: {path}")
    return path


def cmd_carousel(args):
    logger.info(f"Generating carousel: {args.title}")

    brand = None
    if args.brand:
        logger.info(f"Loading brand manual: {args.brand}")
        brand = cargar_brand_manual(args.brand)
        logger.info(f"Brand: {brand['nombre']}")

    if not brand:
        brand = crear_brand_manual_ejemplo()
        logger.info("Using example brand manual")

    points = args.points if args.points else [f"Point {i+1}" for i in range(args.slides - 2)]

    brand_name = brand['nombre'].lower().replace(" ", "_") if brand else "general"
    ensure_output_dir()
    output_path = OUTPUT_DIR / brand_name / "carousels"
    output_path.mkdir(parents=True, exist_ok=True)

    images = generate_carousel(args.title, points, brand, output_path, args.slides)

    logger.info(f"Carousel generated: {len(images)} slides in {output_path}")
    return images


def cmd_thumbnail(args):
    logger.info(f"Generating YouTube thumbnail")

    brand = None
    if args.brand:
        logger.info(f"Loading brand manual: {args.brand}")
        brand = cargar_brand_manual(args.brand)
        logger.info(f"Brand: {brand['nombre']}")

    if not brand:
        brand = crear_brand_manual_ejemplo()
        logger.info("Using example brand manual")

    path = generate_thumbnail(args.title, brand, args.tone)

    # Move to brand folder
    brand_name = brand['nombre'].lower().replace(" ", "_") if brand else "general"
    ensure_output_dir()
    final_dir = OUTPUT_DIR / brand_name
    final_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Thumbnail saved: {path}")
    return path


def cmd_video(args):
    logger.info(f"Generating video: {args.prompt}")

    brand = None
    if args.brand:
        logger.info(f"Loading brand manual: {args.brand}")
        brand = cargar_brand_manual(args.brand)
        logger.info(f"Brand: {brand['nombre']}")

    video_path = generate_video(
        args.prompt,
        duration=args.duration,
        aspect=args.aspect,
        language=args.language,
        brand=brand,
    )

    if video_path:
        brand_name = brand['nombre'].lower().replace(" ", "_") if brand else "general"
        ensure_output_dir()
        final_dir = OUTPUT_DIR / brand_name
        final_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Video saved: {video_path}")
    else:
        logger.warning("Video generated but output file not found")

    return video_path


def cmd_batch(args):
    logger.info(f"Generating batch from: {args.file}")

    with open(args.file, "r", encoding="utf-8") as f:
        posts = json.load(f)

    brand = None
    if args.brand:
        logger.info(f"Loading brand manual: {args.brand}")
        brand = cargar_brand_manual(args.brand)
        logger.info(f"Brand: {brand['nombre']}")

    results = []
    for i, post in enumerate(posts, 1):
        logger.info(f"--- Post {i}/{len(posts)} ---")
        post_type = post.get("tipo", "instagram_post")
        prompt = post.get("prompt", "")

        try:
            format_data = cargar_formato(post_type)
        except FileNotFoundError:
            format_data = {"ancho": 1024, "alto": 1024}

        if brand:
            prompt_complete = build_prompt(prompt, brand, format_data)
        else:
            prompt_complete = prompt

        img = generate_image(prompt_complete, width=format_data["ancho"], height=format_data["alto"])

        brand_name = brand['nombre'].lower().replace(" ", "_") if brand else "general"
        ensure_output_dir()
        final_dir = OUTPUT_DIR / brand_name
        final_dir.mkdir(parents=True, exist_ok=True)

        clean_name = prompt.lower().replace(" ", "_")[:50]
        filename = f"{post_type}_{i:03d}_{clean_name}.png"
        path = final_dir / filename
        save_image(img, path)
        results.append(str(path))
        logger.info(f"Saved: {path}")

    logger.info(f"Batch completed: {len(results)} images generated")
    return results


def cmd_formats(args):
    formats = listar_formatos()
    logger.info(f"Available formats ({len(formats)})")

    for fmt in formats:
        platforms = ", ".join(fmt["plataformas"])
        print(f"  {fmt['nombre']:<25} {fmt['ancho']:>5}x{fmt['alto']:<5}  [{plataformas}]")

    return formats


def cmd_verify(args):
    logger.info("Verifying generation engines")

    results = verify_engines()

    for engine, info in results.items():
        status = info["status"]
        symbol = "OK" if status == "ok" else "FAIL"
        logger.info(f"  [{symbol}] {engine}: {info.get('mensaje', status)}")

    mpt_status = verify_money_printer_turbo()
    symbol = "OK" if mpt_status["status"] == "ok" else "INFO"
    logger.info(f"  [{symbol}] money_printer_turbo: {mpt_status['mensaje']}")

    return results


def cmd_brand(args):
    if args.create:
        logger.info(f"Creating brand manual: {args.create}")
        brand = crear_brand_manual_ejemplo()
        brand["nombre"] = args.create
        path = BRAND_DIR / f"{args.create.lower().replace(' ', '_')}.json"
        guardar_brand_manual(brand, path)
        logger.info(f"Brand manual created: {path}")
        logger.info("Edit the file to customize colors, style, etc.")
        return path

    if args.list:
        logger.info("Available brand manuals:")
        for file in sorted(BRAND_DIR.glob("*.json")):
            with open(file, "r", encoding="utf-8") as f:
                m = json.load(f)
            logger.info(f"  {file.stem}: {m.get('nombre', 'Sin nombre')}")
        return

    print("\nUsage:")
    print("  python main.py brand --create 'BrandName'")
    print("  python main.py brand --list")


def main():
    parser = argparse.ArgumentParser(
        prog="ad_studio",
        description="Visual Content Generator for Social Media",
    )
    subparsers = parser.add_subparsers(dest="comando", help="Available commands")

    p_image = subparsers.add_parser("image", help="Generate image for a social network")
    p_image.add_argument("--type", required=True, help="Format type (e.g., instagram_post)")
    p_image.add_argument("--prompt", required=True, help="Image description")
    p_image.add_argument("--brand", help="Path to brand manual JSON")
    p_image.add_argument("--model", default="schnell", choices=["schnell", "dev", "kontext"])
    p_image.set_defaults(func=cmd_image)

    p_carousel = subparsers.add_parser("carousel", help="Generate carousel slide-by-slide")
    p_carousel.add_argument("--title", required=True, help="Carousel title")
    p_carousel.add_argument("--points", nargs="+", help="Points/ideas per slide")
    p_carousel.add_argument("--slides", type=int, default=5, help="Number of slides (default: 5)")
    p_carousel.add_argument("--brand", help="Path to brand manual JSON")
    p_carousel.set_defaults(func=cmd_carousel)

    p_thumb = subparsers.add_parser("thumbnail", help="Generate YouTube thumbnail")
    p_thumb.add_argument("--title", required=True, help="Title of the video")
    p_thumb.add_argument("--brand", help="Path to brand manual JSON")
    p_thumb.add_argument("--tone", default="professional",
                         choices=["professional", "casual", "surprise", "curious", "direct"])
    p_thumb.set_defaults(func=cmd_thumbnail)

    p_video = subparsers.add_parser("video", help="Generate short video (MoneyPrinterTurbo)")
    p_video.add_argument("--prompt", required=True, help="Video theme")
    p_video.add_argument("--duration", type=int, default=15, help="Duration in seconds")
    p_video.add_argument("--aspect", default="9:16", choices=["9:16", "16:9"])
    p_video.add_argument("--language", default="en", help="Script language")
    p_video.add_argument("--brand", help="Path to brand manual JSON")
    p_video.set_defaults(func=cmd_video)

    p_batch = subparsers.add_parser("batch", help="Generate batch of images from JSON")
    p_batch.add_argument("--file", required=True, help="Path to JSON file with posts")
    p_batch.add_argument("--brand", help="Path to brand manual JSON")
    p_batch.set_defaults(func=cmd_batch)

    p_formats = subparsers.add_parser("formats", help="List available formats")
    p_formats.set_defaults(func=cmd_formats)

    p_verify = subparsers.add_parser("verify", help="Verify available engines")
    p_verify.set_defaults(func=cmd_verify)

    p_brand = subparsers.add_parser("brand", help="Manage brand manuals")
    p_brand.add_argument("--create", help="Create new brand manual with name")
    p_brand.add_argument("--list", action="store_true", help="List brand manuals")
    p_brand.set_defaults(func=cmd_brand)

    args = parser.parse_args()

    if not args.comando:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
