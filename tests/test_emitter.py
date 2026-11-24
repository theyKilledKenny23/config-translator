"""Тесты модуля src.emitter."""

from src.emitter import to_yaml


def test_single_number():
    """Одно числовое значение."""
    data = [{"name": "size", "value": 3.5}]
    result = to_yaml(data)
    assert result == "size: 3.5\n"


def test_multiple_values():
    """Несколько значений."""
    data = [
        {"name": "width", "value": 1920.0},
        {"name": "height", "value": 1080.0},
    ]
    result = to_yaml(data)
    assert "width: 1920.0" in result
    assert "height: 1080.0" in result


def test_array_value():
    """Значение в виде массива."""
    data = [{"name": "point", "value": [1.0, 2.0, 3.0]}]
    result = to_yaml(data)
    assert "point:" in result
    assert "- 1.0" in result
    assert "- 2.0" in result
    assert "- 3.0" in result


def test_empty_data():
    """Пустой список объявлений."""
    result = to_yaml([])
    assert result == "{}\n"