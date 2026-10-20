#!/usr/bin/env python3
"""
backup.py — бэкап папки с ротацией старых копий.

Пример:
    python backup.py --src /home/user/data --dst /mnt/backups --keep 5
"""
import argparse
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("backup")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Бэкап папки с ротацией старых копий")
    parser.add_argument("--src", required=True, help="Папка, которую нужно забэкапить")
    parser.add_argument("--dst", required=True, help="Куда складывать архивы")
    parser.add_argument("--keep", type=int, default=5, help="Сколько последних архивов хранить (по умолчанию 5)")
    parser.add_argument(
        "--format", default="zip", choices=["zip", "gztar", "tar"], help="Формат архива (по умолчанию zip)"
    )
    return parser.parse_args()


def make_backup(src: Path, dst: Path, archive_format: str) -> Path:
    if not src.exists():
        raise FileNotFoundError(f"Источник не найден: {src}")
    dst.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_base = dst / f"{src.name}_{timestamp}"

    logger.info("Создаю архив %s из %s ...", archive_base, src)
    archive_path = shutil.make_archive(
        str(archive_base), archive_format, root_dir=src.parent, base_dir=src.name
    )
    logger.info("Готово: %s", archive_path)
    return Path(archive_path)


def rotate_backups(dst: Path, prefix: str, keep: int) -> None:
    backups = sorted(
        (p for p in dst.iterdir() if p.is_file() and p.name.startswith(prefix)),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for old_backup in backups[keep:]:
        logger.info("Удаляю старый бэкап: %s", old_backup)
        old_backup.unlink()


def main() -> None:
    args = parse_args()
    src = Path(args.src).resolve()
    dst = Path(args.dst).resolve()

    try:
        make_backup(src, dst, args.format)
        rotate_backups(dst, prefix=src.name, keep=args.keep)
    except Exception as exc:
        logger.error("Бэкап не выполнен: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
