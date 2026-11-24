"""Точка входа CLI для транслятора конфигурационного языка."""

import argparse
import sys

from src.emitter import to_yaml
from src.parser import parse
from src.resolver import resolve


def main():
    """Главная функция CLI."""
    parser = argparse.ArgumentParser(
        description="Транслятор учебного конфигурационного языка в YAML",
    )
    parser.add_argument(
        "input",
        help="Путь к входному файлу конфигурации",
    )
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as f:
        source = f.read()

    try:
        ast = parse(source)
        resolved = resolve(ast)
        output = to_yaml(resolved)
        print(output, end="")
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()