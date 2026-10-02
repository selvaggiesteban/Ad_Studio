import subprocess
import shutil
import logging
from pathlib import Path

from config import MONEY_PRINTER_TURBO_PATH

logger = logging.getLogger("ad_studio")

def verify_money_printer_turbo():
    if not MONEY_PRINTER_TURBO_PATH:
        return {
            "status": "not_configured",
            "message": "MONEY_PRINTER_TURBO_PATH not configured in .env",
        }

    path = Path(MONEY_PRINTER_TURBO_PATH)
    if not path.exists():
        return {
            "status": "not_found",
            "message": f"Directory not found: {path}",
        }

    cli = path / "cli.py"
    config = path / "config.toml"
    config_example = path / "config.example.toml"

    if not cli.exists():
        return {
            "status": "invalid",
            "message": "cli.py not found in the directory",
        }

    if not config.exists() and not config_example.exists():
        return {
            "status": "not_configured",
            "message": "Missing config.toml (copy from config.example.toml)",
        }

    return {
        "status": "ok",
        "message": "MoneyPrinterTurbo found and configured",
        "path": str(path),
    }


def generate_video(prompt, duration=15, aspect="9:16", language="en", brand=None):
    status = verify_money_printer_turbo()
    if status["status"] != "ok":
        raise RuntimeError(
            f"MoneyPrinterTurbo unavailable: {status['message']}. "
            f"Configure MONEY_PRINTER_TURBO_PATH in .env"
        )

    mpt_path = Path(status["path"])
    cli_path = mpt_path / "cli.py"

    args = [
        "python",
        str(cli_path),
        "--video-subject", prompt,
        "--video-aspect", aspect,
        "--video-language", language,
        "--stop-at", "video",
    ]

    logger.info(f"  [MoneyPrinterTurbo] Generating video...")
    logger.info(f"  Prompt: {prompt}")
    logger.info(f"  Aspect: {aspect}")

    result = subprocess.run(
        args,
        cwd=str(mpt_path),
        capture_output=True,
        text=True,
        timeout=600,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"MoneyPrinterTurbo failed (code {result.returncode}):\n"
            f"{result.stderr}"
        )

    logger.info(f"  [MoneyPrinterTurbo] Video generated successfully")

    output_dir = mpt_path / "output"
    if output_dir.exists():
        videos = sorted(output_dir.glob("*.mp4"), key=lambda f: f.stat().st_mtime, reverse=True)
        if videos:
            return videos[0]

    return None
