import functools

from . import nodes
from .exceptions import (
    UnexpectedTokenError,
    SubNodeError,
)

@functools.lru_cache()
def class_map():
    subclasses = [s for s in BaseParser.__subclasses__() if s.node_class]
    subclasses = sorted(subclasses, key=lambda cls: cls.priority, reverse=True)
    return {cls.node_class.id: cls for cls in subclasses}


def indexed(method):
    def surrogate(self):
        first = self.stream.peek()
        node = method(self)
        if not node:
            return
        last = self.stream.peek(-1)
        node.index = first.index[0], last.index[1]
        node.text = self.stream.text
        return node

    return surrogate


class BaseParser:
    priority = 0
    node_class = None

    def __init__(self, stream):
        self.stream = stream

    def parse_object(self):
        parser_ids = class_map().keys()
        node = None
        for parser_id in parser_ids:
            method = getattr(self, "parse_" + parser_id)
            node = method()
            if node:
                break
        if node:
            self._parse_subnode(node)
        return node

    def _parse_subnode(self, node):
        if not self.stream.is_next("/"):
            return
        separator = self.stream.read()
        obj = self.parse_object()
        if not obj:
            raise SubNodeError(separator.index[0])
        node.add(obj)
        self._parse_subnode(obj)

    def parse_objects(self, node):
        while True:
            obj = self.parse_object()
            if not obj:
                break
            node.add(obj)

    def __getattr__(self, attr_name):
        if not attr_name.startswith("parse_"):
            raise AttributeError("Invalid parsing method.")
        parser_id = attr_name.replace("parse_", "")
        subparsers = class_map()
        if parser_id not in subparsers:
            raise AttributeError("Invalid parsing id.")
        parser_class = subparsers[parser_id]
        return parser_class(self.stream).parse


class Parser(BaseParser):
    @indexed
    def parse(self):
        node = nodes.RootNode()
        self.parse_objects(node)
        if not self.stream.is_eof():
            index = self.stream.peek().index[0]
            raise UnexpectedTokenError(index)
        return node


class StructParser:
    @indexed
    def parse(self):
        start_token, end_token = self.delimiters
        if not self.stream.is_next(start_token):
            return
        node = self.node_class()
        self.stream.read(start_token)
        self._parse_key(node)
        self.parse_objects(node)
        self.stream.read(end_token)
        return node

    def _parse_key(self, node):
        if self.stream.is_next(":"):
            self.stream.read()
        else:
            node.key = self.parse_object()


class ScopeParser(BaseParser, StructParser):
    node_class = nodes.ScopeNode
    delimiters = "()"


class QueryParser(BaseParser, StructParser):
    node_class = nodes.QueryNode
    delimiters = "{}"


class ListParser(BaseParser):
    node_class = nodes.ListNode
    delimiters = "[]"

    @indexed
    def parse(self):
        start_token, end_token = self.delimiters
        if not self.stream.is_next(start_token):
            return
        node = self.node_class()
        self.stream.read(start_token)
        self._parse_items(node)
        self.stream.read(end_token)
        return node

    def _parse_items(self, node):
        while True:
            obj = self.parse_object()
            if not obj:
                break
            node.add(obj)


class NameParser(BaseParser):
    node_class = nodes.NameNode

    @indexed
    def parse(self):
        if not self.stream.is_next("name"):
            return
        node = self.node_class()
        node.name = self.stream.read("name").value
        return node


class PrefixedNameParser:
    @indexed
    def parse(self):
        if not self.stream.is_next(self.prefix):
            return
        self.stream.read()
        node = self.node_class()
        node.name = self.stream.read("name").value
        return node


class AttributeParser(BaseParser, PrefixedNameParser):
    node_class = nodes.AttributeNode
    prefix = "@"


class FlagParser(BaseParser, PrefixedNameParser):
    node_class = nodes.FlagNode
    prefix = "!"


class UIDParser(BaseParser, PrefixedNameParser):
    node_class = nodes.UIDNode
    prefix = "#"


class VariableParser(BaseParser, PrefixedNameParser):
    node_class = nodes.VariableNode
    prefix = "$"


class FormatParser(BaseParser, PrefixedNameParser):
    node_class = nodes.FormatNode
    prefix = "%"


class DocParser(BaseParser, PrefixedNameParser):
    node_class = nodes.DocNode
    prefix = "?"


class RangeParser(BaseParser):
    node_class = nodes.RangeNode
    priority = 2

    @indexed
    def parse(self):
        _range = self._parse_range()
        if not _range:
            return
        node = nodes.RangeNode()
        node.value = _range
        return node

    def _parse_range(self):
        start = end = None
        current = self.stream.peek()
        next = self.stream.peek(1)
        if current.id == "..":
            self.stream.read()
            end = self.stream.read("int").value
        elif current.id == "int" and next.id == "..":
            start = self.stream.read().value
            self.stream.read("..")
            if self.stream.is_next("int"):
                end = self.stream.read().value
        else:
            return
        return (start, end)


class LiteralParser:
    @indexed
    def parse(self):
        if not self.stream.is_next(self.node_class.id):
            return
        node = self.node_class()
        node.value = self.stream.read().value
        return node


class FloatParser(BaseParser, LiteralParser):
    node_class = nodes.FloatNode
    priority = 1


class IntParser(BaseParser, LiteralParser):
    node_class = nodes.IntNode


class StringParser(BaseParser, LiteralParser):
    node_class = nodes.StringNode


class BooleanParser(BaseParser, LiteralParser):
    node_class = nodes.BooleanNode


class WildcardParser(BaseParser):
    node_class = nodes.WildcardNode

    @indexed
    def parse(self):
        if self.stream.is_next("*"):
            self.stream.read()
            return self.node_class()
        return
