"""Синтаксический разбор учебного конфигурационного языка."""

from lark import Lark, Transformer


_GRAMMAR = r"""
    start: decl*
    decl: "var" NAME value ";"
    ?value: NUMBER          -> number
          | array
          | "|" NAME "|"    -> ref
    array: "({" [value ("," value)*] "})"

    NUMBER: /[+-]?\d+\.\d+/
    NAME:   /[a-z]+/

    COMMENT: /\*>[^\n]*/
    %import common.WS
    %ignore WS
    %ignore COMMENT
"""


class _TreeBuilder(Transformer):
    """Трансформирует дерево Lark в Python-структуры."""

    def number(self, children):
        """Преобразует лексему числа в float."""
        return float(children[0])

    def ref(self, children):
        """Помечает подстановку |имя| для resolver."""
        return ("ref", str(children[0]))

    def array(self, children):
        """Собирает элементы массива в список."""
        return list(children)

    def decl(self, children):
        """Собирает объявление var имя значение;."""
        return ("var", str(children[0]), children[1])

    def start(self, children):
        """Возвращает список объявлений как корень AST."""
        return list(children)


def build_parser():
    """Создаёт и возвращает Lark-парсер."""
    return Lark(_GRAMMAR, parser="lalr", maybe_placeholders=False)


_PARSER = build_parser()


def parse(text):
    """Разбирает исходный текст в AST."""
    tree = _PARSER.parse(text)
    return _TreeBuilder().transform(tree)