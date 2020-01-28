from ..exceptions import ParsingError
from .stream import Stream
from .nodes import (
    RootNode,
    RuleNode,
    StringNode,
    PatternNode,
    ZeroManyNode,
    OneManyNode,
    OneOfNode,
    SequenceNode,
    OptionalNode,
)


class Symbol:
    def __init__(self, id, parser):
        self.id = id
        self.parser = parser


# ZERO MANY SYMBOL ==========================================

class ZeroMany(Symbol):
    def __init__(self, *rules):
        self.rules = rules

    # HELPER FUNCTION
    def _parse_rules(self, context, node):
        index = context.stream.save()
        try:
            for rule in self.rules:
                node.add(rule.parser(context))
        except ParsingError as error:
            context.stream.restore(index)
            raise error
        return node

    def parser(self, context):
        node = ZeroManyNode()
        while True:
            try:
                node = self._parse_rules(context, node)
            except ParsingError:
                break
        return node


# SEQUENCE SYMBOL ==========================================

class Seq(Symbol):
    def __init__(self, *rules):
        self.rules = rules

    def parser(self, context):
        node = SequenceNode()
        index = context.stream.save()
        try:
            for rule in self.rules:
                node.add(rule.parser(context))
        except ParsingError as error:
            context.stream.restore(index)
            raise error
        return node


# ONE MANY SYMBOL ==========================================

class OneMany(Symbol):
    def __init__(self, *rules):
        self.rules = rules

    def parser(self, context):
        node = OneManyNode()
        while True:
            try:
                for rule in self.rules:
                    node.add(rule.parser(context))
            except ParsingError:
                break
        if len(node):  # TODO: remove this check
            return node
        raise ParsingError


# ONE OF SYMBOL ==========================================

class OneOf(Symbol):
    def __init__(self, *rules):
        self.rules = rules
        # TODO: use `rules` to build error messages

    def parser(self, context):
        node = OneOfNode()
        for rule in self.rules:
            try:
                node.add(rule.parser(context))
                return node
            except ParsingError:
                pass
        raise ParsingError


# OPTIONAL SYMBOL ==========================================

class Opt(Symbol):
    def __init__(self, rule):
        self.rule = rule

    def parser(self, context):
        node = OptionalNode()
        try:
            node.add(self.rule.parser(context))
        except ParsingError:
            pass
        return node


# RULE SYMBOL ==========================================

class Rule(Symbol):
    def __init__(self, id):
        self.id = id

    def parser(self, context):
        rule = context.symbols[id]
        node = RuleNode(id)
        index = context.stream.save()
        try:
            node.add(rule.parser(context))
        except ParsingError as error:
            context.stream.restore(index)
            raise error
        return node


# GRAMMAR ==========================================

class Context:
    def __init__(self, **kw):
        self.symbols = kw.get('symbols', {})
        self.skip_symbols = kw.get('skip_symbols', {})
        self.stream = kw.get('stream', Stream())


class Grammar:
    def __init__(self):
        self.symbols = {}
        self.skip_symbols = {}

    def set(self, id, rule):
        self.symbols[id] = rule

    def parse(self, text):
        stream = Stream(text)
        rule = next(iter(self.symbols.values()))
        context = Context(
            skip_symbols=self.skip_symbols,
            symbols=self.symbols,
            stream=stream
        )
        tree = RootNode()
        tree.add(rule.parser(context))
        self._skip_symbols(context)
        if not stream.eof:
            raise ParsingError
        return tree

    def skip(self, id, string):
        def skip_rule_parser(context):
            try:
                context.stream.read_pattern(string)
            except ParsingError:
                return

        self.skip_symbols[id] = Symbol(id, skip_rule_parser)

    def p(self, string):
        def pattern_parser(context):
            self._skip_symbols(context.stream)
            text, index = context.stream.read_pattern(string)
            return PatternNode(text, index)
        return Symbol(string, pattern_parser)

    def s(self, string):
        def string_parser(context):
            self._skip_symbols(context.stream)
            text, index = context.stream.read_string(string)
            return StringNode(text, index)
        return Symbol(string, string_parser)

    def _skip_symbols(self, context):
        rules = self.skip_symbols.values()
        while True:
            skipped = [True for rule in rules if rule.parser(context)]
            if len(skipped) == 0:
                break
