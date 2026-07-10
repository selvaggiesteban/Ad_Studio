import subprocess
import shutil
from pathlib import Path

from config import MONEY_PRINTER_TURBO_PATH


def verificar_money_printer_turbo():
    if not MONEY_PRINTER_TURBO_PATH:
        return {
            "status": "no_configurado",
            "mensaje": "MONEY_PRINTER_TURBO_PATH no configurado en .env",
        }

    ruta = Path(MONEY_PRINTER_TURBO_PATH)
    if not ruta.exists():
        return {
            "status": "no_encontrado",
            "mensaje": f"Directorio no encontrado: {ruta}",
        }

    cli = ruta / "cli.py"
    config = ruta / "config.toml"
    config_ejemplo = ruta / "config.example.toml"

    if not cli.exists():
        return {
            "status": "invalido",
            "mensaje": "cli.py no encontrado en el directorio",
        }

    if not config.exists() and not config_ejemplo.exists():
        return {
            "status": "sin_configurar",
            "mensaje": "Falta config.toml (copiar de config.example.toml)",
        }

    return {
        "status": "ok",
        "mensaje": "MoneyPrinterTurbo encontrado y configurado",
        "ruta": str(ruta),
    }


def generar_video(prompt, duracion=15, aspecto="9:16", idioma="es", marca=None):
    estado = verificar_money_printer_turbo()
    if estado["status"] != "ok":
        raise RuntimeError(
            f"MoneyPrinterTurbo no disponible: {estado['mensaje']}. "
            f"Configura MONEY_PRINTER_TURBO_PATH en .env"
        )

    ruta_mpt = Path(estado["ruta"])
    cli_path = ruta_mpt / "cli.py"

    args = [
        "python",
        str(cli_path),
        "--video-subject", prompt,
        "--video-aspect", aspecto,
        "--video-language", idioma,
        "--stop-at", "video",
    ]

    print(f"  [MoneyPrinterTurbo] Generando video...")
    print(f"  Prompt: {prompt}")
    print(f"  Aspecto: {aspecto}")

    resultado = subprocess.run(
        args,
        cwd=str(ruta_mpt),
        capture_output=True,
        text=True,
        timeout=600,
    )

    if resultado.returncode != 0:
        raise RuntimeError(
            f"MoneyPrinterTurbo fallo (codigo {resultado.returncode}):\n"
            f"{resultado.stderr}"
        )

    print(f"  [MoneyPrinterTerbo] Video generado exitosamente")

    output_dir = ruta_mpt / "output"
    if output_dir.exists():
        videos = sorted(output_dir.glob("*.mp4"), key=lambda f: f.stat().st_mtime, reverse=True)
        if videos:
            return videos[0]

    return None
