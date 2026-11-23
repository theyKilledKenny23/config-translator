"""Тесты модуля src.parser."""

import pytest
from lark.exceptions import LarkError

from src.parser import parse


def test_single_number_declaration():
    """Одно объявление с числом."""
    ast = parse("var size 3.5;")
    assert ast == [("var", "size", 3.5)]


def test_negative_and_positive_numbers():
    """Числа со знаком."""
    ast = parse("var a -2.5;\nvar b +0.1;")
    assert ast == [
        ("var", "a", -2.5),
        ("var", "b", 0.1),
    ]


def test_array_declaration():
    """Объявление с массивом."""
    ast = parse("var point ({ 1.0, 2.5, 3.0 });")
    assert ast == [("var", "point", [1.0, 2.5, 3.0])]


def test_empty_array():
    """Пустой массив."""
    ast = parse("var empty ({});")
    assert ast == [("var", "empty", [])]


def test_nested_arrays():
    """Вложенные массивы."""
    ast = parse("var m ({ ({ 1.0, 2.0 }), ({ 3.0 }) });")
    assert ast == [("var", "m", [[1.0, 2.0], [3.0]])]


def test_reference_substitution():
    """Подстановка |имя|."""
    ast = parse("var x |size|;")
    assert ast == [("var", "x", ("ref", "size"))]


def test_reference_in_array():
    """Подстановка внутри массива."""
    ast = parse("var center ({ |width|, |height| });")
    assert ast == [
        ("var", "center", [("ref", "width"), ("ref", "height")]),
    ]


def test_comment_ignored():
    """Комментарии игнорируются."""
    src = (
        "*> это комментарий\n"
        "var size 3.5; *> inline comment\n"
    )
    ast = parse(src)
    assert ast == [("var", "size", 3.5)]


def test_multiple_declarations():
    """Несколько объявлений подряд."""
    src = (
        "var width 1920.0;\n"
        "var height 1080.0;\n"
        "var center ({ |width|, |height| });\n"
    )
    ast = parse(src)
    assert len(ast) == 3
    assert ast[0] == ("var", "width", 1920.0)
    assert ast[2][2] == [("ref", "width"), ("ref", "height")]


def test_syntax_error_on_missing_semicolon():
    """Отсутствие ';' вызывает ошибку."""
    with pytest.raises(LarkError):
        parse("var size 3.5")


def test_syntax_error_on_integer_without_dot():
    """Целое число без точки — ошибка."""
    with pytest.raises(LarkError):
        parse("var size 12;")


def test_syntax_error_on_uppercase_name():
    """Имя с заглавной буквой — ошибка."""
    with pytest.raises(LarkError):
        parse("var Size 3.5;")


def test_empty_input():
    """Пустой вход даёт пустой AST."""
    assert parse("") == []
    assert parse("*> только комментарий\n") == []