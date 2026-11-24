"""Сериализация AST в формат YAML."""

import yaml


def to_yaml(data):
    """Преобразует список объявлений в YAML-строку.

    Args:
        data: список словарей вида {"name": имя, "value": значение}.

    Returns:
        YAML-строка с конфигурацией.
    """
    config = {item["name"]: item["value"] for item in data}
    return yaml.dump(config, default_flow_style=False, allow_unicode=True)