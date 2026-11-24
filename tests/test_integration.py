"""Интеграционные тесты полного цикла работы CLI."""

import subprocess
import tempfile
from pathlib import Path

from src.emitter import to_yaml
from src.parser import parse
from src.resolver import resolve


def _run_pipeline(source):
    """Прогоняет исходник через весь пайплайн и возвращает YAML."""
    ast = parse(source)
    resolved = resolve(ast)
    return to_yaml(resolved)


def test_full_cycle_simple():
    """Простой полный цикл: числа и подстановки."""
    source = (
        "var width 1920.0;\n"
        "var height 1080.0;\n"
        "var center ({ |width|, |height| });\n"
    )
    result = _run_pipeline(source)
    assert "width: 1920.0" in result
    assert "height: 1080.0" in result
    assert "- 1920.0" in result
    assert "- 1080.0" in result


def test_full_cycle_nested_arrays():
    """Вложенные массивы и подстановки."""
    source = (
        "var x 1.0;\n"
        "var y 2.0;\n"
        "var z 3.0;\n"
        "var point ({ |x|, |y|, |z| });\n"
        "var line ({ |point|, ({ 4.0, 5.0 }) });\n"
    )
    result = _run_pipeline(source)
    assert "- 1.0" in result
    assert "- 2.0" in result
    assert "- 3.0" in result
    assert "- 4.0" in result
    assert "- 5.0" in result


def test_full_cycle_with_comments():
    """Комментарии игнорируются в полном цикле."""
    source = (
        "*> это комментарий\n"
        "var size 3.5; *> inline comment\n"
        "var half |size|;\n"
    )
    result = _run_pipeline(source)
    assert "size: 3.5" in result
    assert "half: 3.5" in result


def test_full_cycle_undefined_reference():
    """Ошибка при неопределённой константе."""
    source = "var x |missing|;"
    try:
        _run_pipeline(source)
        assert False, "Должна была возникнуть ошибка"
    except ValueError as e:
        assert "Неопределённая константа: missing" in str(e)


def test_full_cycle_cyclic_reference():
    """Ошибка при циклической ссылке."""
    source = (
        "var a |b|;\n"
        "var b |a|;\n"
    )
    try:
        _run_pipeline(source)
        assert False, "Должна была возникнуть ошибка"
    except ValueError as e:
        assert "Циклическая ссылка" in str(e)


def test_cli_with_file():
    """Тест CLI с реальным файлом."""
    source = (
        "var width 1920.0;\n"
        "var height 1080.0;\n"
        "var center ({ |width|, |height| });\n"
    )
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".cfg", delete=False, encoding="utf-8"
    ) as f:
        f.write(source)
        f.flush()
        temp_path = Path(f.name)

    try:
        result = subprocess.run(
            ["python", "-m", "src.cli", str(temp_path)],
            capture_output=True,
            text=True,
            check=True,
        )
        assert "width: 1920.0" in result.stdout
        assert "height: 1080.0" in result.stdout
        assert "- 1920.0" in result.stdout
        assert "- 1080.0" in result.stdout
    finally:
        temp_path.unlink()


def test_cli_with_invalid_file():
    """Тест CLI с несуществующим файлом."""
    result = subprocess.run(
        ["python", "-m", "src.cli", "nonexistent.cfg"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "Ошибка" in result.stderr