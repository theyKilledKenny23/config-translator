"""Модуль разрешения ссылок на константы в AST."""

_RESOLVING = object()


def _resolve_value(value, env, visited):
    """Рекурсивно разрешает значения, подставляя ссылки.

    Args:
        value: float, list или кортеж ("ref", имя).
        env: словарь уже разрешённых констант.
        visited: множество имён в текущей цепочке разрешений.

    Returns:
        Разрешённое значение (float или list).

    Raises:
        ValueError: при неопределённой или циклической ссылке.
    """
    if isinstance(value, list):
        return [_resolve_value(v, env, visited) for v in value]

    if isinstance(value, tuple) and value[0] == "ref":
        name = value[1]
        if name in visited:
            raise ValueError(f"Циклическая ссылка: {name}")
        if name not in env:
            raise ValueError(f"Неопределённая константа: {name}")
        if env[name] is _RESOLVING:
            raise ValueError(f"Циклическая ссылка: {name}")
        return _resolve_value(env[name], env, visited | {name})

    return value


def resolve(ast):
    """Разрешает все ссылки в AST и возвращает список словарей.

    Args:
        ast: список кортежей вида ("var", имя, значение) от парсера.

    Returns:
        Список словарей вида {"name": имя, "value": значение}.
    """
    env = {}
    for decl in ast:
        env[decl[1]] = _RESOLVING

    result = []
    for decl in ast:
        name = decl[1]
        resolved_val = _resolve_value(decl[2], env, set())
        env[name] = resolved_val
        result.append({"name": name, "value": resolved_val})

    return result