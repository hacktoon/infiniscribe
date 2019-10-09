import re

from .exceptions import ParsingError


_parsers = {}


class Token:
    def __init__(self, id, text, index):
        self.id = id
        self.text = text
        self.index = index

    def __eq__(self, token):
        return self.id == token.id

    def __len__(self):
        return len(self.text)

    def __repr__(self):
        return "TOKEN({!r})".format(self.text)

    def __str__(self):
        start, end = self.index
        return self.text[start:end]


class TokenStream:
    def __init__(self, text):
        self.text = text
        self.index = 0

    def save(self):
        return self.index

    def restore(self, index):
        self.index = index

    def parse(self, token_id):
        parser = _parsers[token_id]
        token = parser(self.text, self.index)
        self.index += len(token)
        return token


def token(id, regex=None):
    regex = re.compile(regex or re.escape(id))

    def parser(text, index=0):
        match = regex.match(text, index)
        if match:
            return Token(id, match.group(0), match.span())
        raise ParsingError
    _parsers[id] = parser
    return parser


# MEL GRAMMAR
# TODO: move to file

token("space", r"(\s|;|,)*")
token("comment", r"--[^\n\r]*")
token("string", r"'[^']*'")
token("template-string", r'"[^"]*"')
token("float", r"-?\d*\.\d+([eE][-+]?\d+)?\b")
token("int", r"-?\d+\b")
token("name", r"[a-z]\w*")
token("concept", r"[A-Z]\w*")
token("!=")
token("!")
token("@")
token("$")
token("#")
token("%:")
token("%")
token("?:")
token("?")
token("/")
token(".")
token("..")
token(":")
token("=")
token("><")
token(">=")
token(">")
token("<>")
token("<=")
token("<")
token("*")
token("(")
token(")")
token("{")
token("}")
token("[")
token("]")
