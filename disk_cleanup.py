#!/usr/bin/env python3
"""
disk_cleanup.py — удаляет файлы старше N дней по маске (например, временные файлы или старые логи).

Примеры:
    python disk_cleanup.py --path /tmp --days 14 --pattern "*.tmp" --dry-run
    python disk_cleanup.py --path C:\\Logs --days 30 --pattern "*.log"
"""
import argparse
import logging
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("disk_cleanup")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Удаление старых файлов по маске и возрасту")
    parser.add_argument("--path", required=True, help="Папка для очистки")
    parser.add_argument("--days", type=int, default=30, help="Удалять файлы старше N дней")
    parser.add_argument("--pattern", default="*", help="Маска файлов, например *.log или *.tmp")
    parser.add_argument("--dry-run", action="store_true", help="Только показать, что будет удалено, без удаления")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(args.path)
    if not root.exists():
        logger.error("Папка не найдена: %s", root)
        return

    cutoff = time.time() - args.days * 86400
    total_size = 0
    removed = 0

    for file_path in root.rglob(args.pattern):
        if not file_path.is_file():
            continue
        if file_path.stat().st_mtime >= cutoff:
            continue

        size = file_path.stat().st_size
        if args.dry_run:
            logger.info("[DRY RUN] Удалил бы: %s (%.1f КБ)", file_path, size / 1024)
        else:
            try:
                file_path.unlink()
                logger.info("Удалён: %s (%.1f КБ)", file_path, size / 1024)
            except Exception as exc:
                logger.warning("Не удалось удалить %s: %s", file_path, exc)
                continue

        total_size += size
        removed += 1

    action = "Будет удалено" if args.dry_run else "Удалено"
    logger.info("%s файлов: %d, освобождено места: %.2f МБ", action, removed, total_size / (1024 * 1024))


if __name__ == "__main__":
    main()
