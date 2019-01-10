from . import nodes
from .exceptions import (
    UnexpectedTokenError,
    SubNodeError,
)


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
    def __init__(self, stream):
        self.stream = stream
        self.PARSER_MAP = {
            "string": StringParser,
            "boolean": BooleanParser,
            "wildcard": WildcardParser,
            "float": FloatParser,
            "int": IntParser,
            "range": RangeParser,
            "name": NameParser,
            "flag": FlagParser,
            "attribute": AttributeParser,
            "uid": UIDParser,
            "variable": VariableParser,
            "format": FormatParser,
            "doc": DocParser,
            "scope": ScopeParser,
            "query": QueryParser,
            "list": ListParser,
        }

    def parse_object(self):
        methods = [
            self.parse_range,
            self.parse_float,
            self.parse_int,
            self.parse_boolean,
            self.parse_string,
            self.parse_name,
            self.parse_flag,
            self.parse_attribute,
            self.parse_uid,
            self.parse_variable,
            self.parse_format,
            self.parse_doc,
            self.parse_scope,
            self.parse_query,
            self.parse_list,
            self.parse_wildcard,
        ]
        node = None
        for method in methods:
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
        if parser_id not in self.PARSER_MAP:
            raise AttributeError("Invalid parsing id.")
        parser_class = self.PARSER_MAP[parser_id]
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
    delimiters = "[]"

    @indexed
    def parse(self):
        start_token, end_token = self.delimiters
        if not self.stream.is_next(start_token):
            return
        node = nodes.ListNode()
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
    @indexed
    def parse(self):
        if not self.stream.is_next("name"):
            return
        node = nodes.NameNode()
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
    prefix = "@"
    node_class = nodes.AttributeNode


class FlagParser(BaseParser, PrefixedNameParser):
    prefix = "!"
    node_class = nodes.FlagNode


class UIDParser(BaseParser, PrefixedNameParser):
    prefix = "#"
    node_class = nodes.UIDNode


class VariableParser(BaseParser, PrefixedNameParser):
    prefix = "$"
    node_class = nodes.VariableNode


class FormatParser(BaseParser, PrefixedNameParser):
    prefix = "%"
    node_class = nodes.FormatNode


class DocParser(BaseParser, PrefixedNameParser):
    prefix = "?"
    node_class = nodes.DocNode


class FloatParser(BaseParser):
    @indexed
    def parse(self):
        if not self.stream.is_next("float"):
            return
        node = nodes.FloatNode()
        node.value = self.stream.read().value
        return node


class IntParser(BaseParser):
    @indexed
    def parse(self):
        if not self.stream.is_next("int"):
            return
        node = nodes.IntNode()
        node.value = self.stream.read().value
        return node


class RangeParser(BaseParser):
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


class StringParser(BaseParser):
    @indexed
    def parse(self):
        if not self.stream.is_next("string"):
            return
        node = nodes.StringNode()
        node.value = self.stream.read().value
        return node


class BooleanParser(BaseParser):
    @indexed
    def parse(self):
        if not self.stream.is_next("boolean"):
            return
        node = nodes.BooleanNode()
        node.value = self.stream.read().value
        return node


class WildcardParser(BaseParser):
    @indexed
    def parse(self):
        if self.stream.is_next("*"):
            self.stream.read()
            return nodes.WildcardNode()
        return
