#!/usr/bin/env python3
"""
log_parser.py — анализирует лог-файл: считает записи по уровням
(DEBUG/INFO/WARNING/ERROR/...) и показывает самые частые сообщения нужного уровня.

Примеры:
    python log_parser.py --file /var/log/syslog
    python log_parser.py --file app.log --level ERROR --top 10
"""
import argparse
import re
import sys
from collections import Counter
from pathlib import Path

LEVEL_PATTERN = re.compile(r"\b(DEBUG|INFO|WARNING|WARN|ERROR|CRITICAL|FATAL)\b", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Анализ лог-файла: подсчёт по уровням и топ сообщений")
    parser.add_argument("--file", required=True, help="Путь к лог-файлу")
    parser.add_argument("--level", default=None, help="Фильтр по уровню, например ERROR")
    parser.add_argument("--top", type=int, default=10, help="Сколько самых частых строк показать")
    return parser.parse_args()


def read_lines(path: Path):
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            yield line.rstrip("\n")


def main() -> None:
    args = parse_args()
    path = Path(args.file)
    if not path.exists():
        print(f"Файл не найден: {path}", file=sys.stderr)
        sys.exit(1)

    level_counts: Counter = Counter()
    message_counts: Counter = Counter()
    level_filter = args.level.upper() if args.level else None

    for line in read_lines(path):
        match = LEVEL_PATTERN.search(line)
        level = match.group(1).upper() if match else "UNKNOWN"
        level = "WARNING" if level == "WARN" else level
        level_counts[level] += 1

        if level_filter and level == level_filter:
            message_counts[line.strip()] += 1

    print("=== Сводка по уровням ===")
    for level, count in level_counts.most_common():
        print(f"{level:10} {count}")

    if level_filter:
        print(f"\n=== Топ {args.top} сообщений уровня {level_filter} ===")
        if not message_counts:
            print("(ничего не найдено)")
        for message, count in message_counts.most_common(args.top):
            print(f"[{count}x] {message}")


if __name__ == "__main__":
    main()
