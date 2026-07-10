import base64
import io
import time
import json
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


def generar_con_nvidia(prompt, ancho=1024, alto=1024, modelo=DEFAULT_MODEL, seed=None):
    api_key = get_api_key()
    modelo_config = MODELS[modelo]

    if (ancho, alto) not in RESOLUTIONES_VALIDAS:
        closest = min(RESOLUTIONES_VALIDAS, key=lambda r: abs(r[0] - ancho) + abs(r[1] - alto))
        ancho, alto = closest

    payload = {
        "prompt": prompt,
        "width": ancho,
        "height": alto,
        "steps": modelo_config["steps"],
    }
    if seed is not None:
        payload["seed"] = seed

    url = f"{NVIDIA_BASE_URL}/{modelo_config['id']}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=120)
    resp.raise_for_status()
    resultado = resp.json()

    if "artifacts" in resultado:
        img_b64 = resultado["artifacts"][0]["base64"]
    elif "image" in resultado:
        img_b64 = resultado["image"]
    elif "data" in resultado and len(resultado["data"]) > 0:
        img_b64 = resultado["data"][0].get("b64_json", resultado["data"][0].get("url", ""))
    else:
        raise RuntimeError(f"Respuesta inesperada de NVIDIA NIM: {list(resultado.keys())}")

    if img_b64.startswith("http"):
        img_data = requests.get(img_b64, timeout=60).content
    else:
        img_data = base64.b64decode(img_b64)

    return Image.open(io.BytesIO(img_data))


def generar_con_pollinations(prompt, ancho=1024, alto=1024):
    prompt_encoded = requests.utils.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width={ancho}&height={alto}&nologo=true&model=flux"

    resp = requests.get(url, timeout=120)
    resp.raise_for_status()

    return Image.open(io.BytesIO(resp.content))


def generar_imagen(prompt, ancho=1024, alto=1024, modelo=DEFAULT_MODEL, seed=None, intentos=1):
    ultimo_error = None

    if NVIDIA_API_KEY:
        for intento in range(intentos):
            try:
                print(f"  [NVIDIA NIM] Generando con {MODELS[modelo]['name']}...")
                img = generar_con_nvidia(prompt, ancho, alto, modelo, seed)
                print(f"  [NVIDIA NIM] OK")
                return img
            except Exception as e:
                ultimo_error = e
                print(f"  [NVIDIA NIM] Fallo: {e}")
    else:
        print(f"  [NVIDIA NIM] Saltando (no API key configurada)")

    print(f"  [Pollinations] Generando con Flux Schnell...")
    try:
        img = generar_con_pollinations(prompt, ancho, alto)
        print(f"  [Pollinations] OK")
        return img
    except Exception as e:
        ultimo_error = e
        print(f"  [Pollinations] Fallo: {e}")

    raise RuntimeError(f"No se pudo generar la imagen. Ultimo error: {ultimo_error}")


def guardar_imagen(img, ruta, formato="PNG", calidad=95):
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)

    if formato.upper() == "JPG" or formato.upper() == "JPEG":
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.save(ruta, "JPEG", quality=calidad)
    else:
        img.save(ruta, "PNG")

    return ruta


def verificar_motores():
    resultados = {}

    print("Verificando NVIDIA NIM API...")
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
            resultados["nvidia_nim"] = {"status": "ok", "modelo": DEFAULT_MODEL}
        else:
            resultados["nvidia_nim"] = {"status": "error", "mensaje": f"HTTP {resp.status_code}: {resp.text[:200]}"}
    except Exception as e:
        resultados["nvidia_nim"] = {"status": "error", "mensaje": str(e)}

    print("Verificando Pollinations.ai...")
    try:
        resp = requests.get("https://image.pollinations.ai/prompt/test?width=256&height=256&nologo=true", timeout=60)
        if resp.status_code == 200:
            resultados["pollinations"] = {"status": "ok"}
        else:
            resultados["pollinations"] = {"status": "error", "mensaje": f"HTTP {resp.status_code}"}
    except Exception as e:
        resultados["pollinations"] = {"status": "error", "mensaje": str(e)}

    return resultados
