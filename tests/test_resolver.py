"""Тесты модуля src.resolver."""

import pytest

from src.resolver import resolve


def test_simple_substitution():
    """Простая подстановка константы."""
    ast = [
        ("var", "size", 3.5),
        ("var", "half", ("ref", "size")),
    ]
    result = resolve(ast)
    assert result == [
        {"name": "size", "value": 3.5},
        {"name": "half", "value": 3.5},
    ]


def test_substitution_in_array():
    """Подстановка константы внутри массива."""
    ast = [
        ("var", "x", 1.0),
        ("var", "y", 2.0),
        ("var", "point", [("ref", "x"), ("ref", "y")]),
    ]
    result = resolve(ast)
    assert result == [
        {"name": "x", "value": 1.0},
        {"name": "y", "value": 2.0},
        {"name": "point", "value": [1.0, 2.0]},
    ]


def test_nested_substitution():
    """Вложенная подстановка (константа ссылается на константу)."""
    ast = [
        ("var", "a", 10.0),
        ("var", "b", ("ref", "a")),
        ("var", "c", ("ref", "b")),
    ]
    result = resolve(ast)
    assert result == [
        {"name": "a", "value": 10.0},
        {"name": "b", "value": 10.0},
        {"name": "c", "value": 10.0},
    ]


def test_undefined_reference():
    """Ошибка при ссылке на необъявленную константу."""
    ast = [("var", "x", ("ref", "missing"))]
    with pytest.raises(ValueError, match="Неопределённая константа: missing"):
        resolve(ast)


def test_cyclic_reference():
    """Ошибка при циклической ссылке."""
    ast = [
        ("var", "a", ("ref", "b")),
        ("var", "b", ("ref", "a")),
    ]
    with pytest.raises(ValueError, match="Циклическая ссылка"):
        resolve(ast)


def test_empty_ast():
    """Пустой AST возвращается как пустой список."""
    assert resolve([]) == []