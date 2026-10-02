import base64
import io
import time
import json
import logging
from pathlib import Path

import requests
from PIL import Image

from config import (
    NVIDIA_API_KEY,
    NVIDIA_BASE_URL,
    MODELS,
    DEFAULT_MODEL,
    RESOLUTIONES_VALIDAS,
    get_api_key,
)

logger = logging.getLogger("ad_studio")

def generate_with_nvidia(prompt, width=1024, height=1024, model=DEFAULT_MODEL, seed=None):
    api_key = get_api_key()
    model_config = MODELS[model]

    if (width, height) not in RESOLUTIONES_VALIDAS:
        closest = min(RESOLUTIONES_VALIDAS, key=lambda r: abs(r[0] - width) + abs(r[1] - height))
        width, height = closest

    payload = {
        "prompt": prompt,
        "width": width,
        "height": height,
        "steps": model_config["steps"],
    }
    if seed is not None:
        payload["seed"] = seed

    url = f"{NVIDIA_BASE_URL}/{model_config['id']}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=120)
    resp.raise_for_status()
    result = resp.json()

    if "artifacts" in result:
        img_b64 = result["artifacts"][0]["base64"]
    elif "image" in result:
        img_b64 = result["image"]
    elif "data" in result and len(result["data"]) > 0:
        img_b64 = result["data"][0].get("b64_json", result["data"][0].get("url", ""))
    else:
        raise RuntimeError(f"Unexpected response from NVIDIA NIM: {list(result.keys())}")

    if img_b64.startswith("http"):
        img_data = requests.get(img_b64, timeout=60).content
    else:
        img_data = base64.b64decode(img_b64)

    return Image.open(io.BytesIO(img_data))


def generate_with_pollinations(prompt, width=1024, height=1024):
    prompt_encoded = requests.utils.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width={width}&height={height}&nologo=true&model=flux"

    resp = requests.get(url, timeout=120)
    resp.raise_for_status()

    return Image.open(io.BytesIO(resp.content))


def generate_image(prompt, width=1024, height=1024, model=DEFAULT_MODEL, seed=None, attempts=1):
    last_error = None

    if NVIDIA_API_KEY:
        for attempt in range(attempts):
            try:
                logger.info(f"[NVIDIA NIM] Generating with {MODELS[model]['name']}...")
                img = generate_with_nvidia(prompt, width, height, model, seed)
                logger.info("[NVIDIA NIM] OK")
                return img
            except Exception as e:
                last_error = e
                logger.error(f"[NVIDIA NIM] Failed: {e}")
    else:
        logger.info("[NVIDIA NIM] Skipping (no API key configured)")

    logger.info("[Pollinations] Generating with Flux Schnell...")
    try:
        img = generate_with_pollinations(prompt, width, height)
        logger.info("[Pollinations] OK")
        return img
    except Exception as e:
        last_error = e
        logger.error(f"[Pollinations] Failed: {e}")

    raise RuntimeError(f"Could not generate image. Last error: {last_error}")


def save_image(img, path, format="PNG", quality=95):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if format.upper() == "JPG" or format.upper() == "JPEG":
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.save(path, "JPEG", quality=calidad)
    else:
        img.save(path, "PNG")

    return path


def verify_engines():
    results = {}

    logger.info("Verifying NVIDIA NIM API...")
    try:
        api_key = get_api_key()
        url = f"{NVIDIA_BASE_URL}/{MODELS[DEFAULT_MODEL]['id']}"
        payload = {
            "prompt": "test",
            "width": 512,
            "height": 512,
            "steps": 4,
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        if resp.status_code == 200:
            results["nvidia_nim"] = {"status": "ok", "model": DEFAULT_MODEL}
        else:
            results["nvidia_nim"] = {"status": "error", "message": f"HTTP {resp.status_code}: {resp.text[:200]}"}
    except Exception as e:
        results["nvidia_nim"] = {"status": "error", "message": str(e)}

    logger.info("Verifying Pollinations.ai...")
    try:
        resp = requests.get("https://image.pollinations.ai/prompt/test?width=256&height=256&nologo=true", timeout=60)
        if resp.status_code == 200:
            results["pollinations"] = {"status": "ok"}
        else:
            results["pollinations"] = {"status": "error", "message": f"HTTP {resp.status_code}"}
    except Exception as e:
        results["pollinations"] = {"status": "error", "message": str(e)}

    return results
