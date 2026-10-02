from pathlib import Path
import logging
from brand.prompt_builder import build_carousel_prompts
from generators.image_generator import generate_image, save_image

logger = logging.getLogger("ad_studio")

def generate_carousel(title, points, brand, output_path=None, slides=5):
    if len(points) < slides - 2:
        slides = len(points) + 2

    prompts = build_carousel_prompts(title, points, brand, slides)

    if output_path is None:
        from config import ensure_output_dir
        output_path = ensure_output_dir() / "carousels"
    else:
        output_path = Path(output_path)

    output_path.mkdir(parents=True, exist_ok=True)

    generated_images = []
    for info in prompts:
        slide_num = info["slide"]
        slide_type = info["tipo"]
        prompt = info["prompt"]

        logger.info(f"  Slide {slide_num}/{slides} ({slide_type})...")
        img = generate_image(prompt, width=1080, height=1350)

        filename = f"slide_{slide_num:02d}_{slide_type}.png"
        file_path = output_path / filename
        save_image(img, file_path)
        generated_images.append(file_path)
        logger.info(f"  Saved: {file_path}")

    return generated_images
