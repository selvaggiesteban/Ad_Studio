from pathlib import Path
import logging
from brand.prompt_builder import build_thumbnail_prompt
from generators.image_generator import generate_image, save_image

logger = logging.getLogger("ad_studio")

def generate_thumbnail(title, brand, tone="professional", output_path=None):
    prompt = build_thumbnail_prompt(title, brand, tone)

    if output_path is None:
        from config import ensure_output_dir
        output_path = ensure_output_dir()
    else:
        output_path = Path(output_path)

    output_path.mkdir(parents=True, exist_ok=True)

    clean_name = title.lower().replace(" ", "_")[:50]
    filename = f"thumbnail_{clean_name}.png"
    file_path = output_path / filename

    logger.info(f"  Generating thumbnail: {title}")
    img = generate_image(prompt, width=1280, height=720)
    save_image(img, file_path)
    logger.info(f"  Saved: {file_path}")

    return file_path
