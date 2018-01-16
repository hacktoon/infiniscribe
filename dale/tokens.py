import re


def classes():
    token_types = []
    for cls in Token.__subclasses__():
        token_types.append(cls)
    return sorted(token_types, key=lambda cls: cls.priority, reverse=True)


class Token:
    id = ''
    regex = None
    skip = False
    priority = 0

    def __init__(self, match='', start=0, end=0):
        self.match = match
        self.start = start
        self.end = end

    @property
    def value(self):
        return self.match

    def __repr__(self):
        return self.match


class StringToken(Token):
    id = 'string'
    regex = re.compile('{}|{}'.format(r"'[^']*'", r'"[^"]*"'))

    @property
    def value(self):
        return self.match[1:-1]


class FloatToken(Token):
    id = 'float'
    regex = re.compile(r'[-+]?\d*\.\d+([eE][-+]?\d+)?\b')
    priority = 2

    @property
    def value(self):
        return float(self.match)


class IntToken(Token):
    id = 'int'
    regex = re.compile(r'[-+]?\d+\b')
    priority = 1

    @property
    def value(self):
        return int(self.match)


class BooleanToken(Token):
    id = 'boolean'
    regex = re.compile(r'(true|false)\b')
    priority = 2

    @property
    def value(self):
        return {'true': True, 'false': False}[self.match]


class WhitespaceToken(Token):
    id = 'whitespace'
    regex = re.compile(r'[ ,\n\r\t\x0b\x0c]+')
    skip = True


class CommentToken(Token):
    id = 'comment'
    regex = re.compile(r'#[^\n\r]*')
    skip = True


class NameToken(Token):
    id = 'name'
    regex = re.compile(r'[_a-zA-Z]\w*(-[_a-zA-Z]\w*)?')
    priority = 1


class DotToken(Token):
    id = '.'
    regex = re.compile(r'\.')


class EnvToken(Token):
    id = '$'
    regex = re.compile(r'\$')


class FileToken(Token):
    id = '<'
    regex = re.compile('<')


class AtToken(Token):
    id = '@'
    regex = re.compile('@')


class ColonToken(Token):
    id = ':'
    regex = re.compile(':')


class LeftParenthesisToken(Token):
    id = '('
    regex = re.compile(r'\(')


class RightParenthesisToken(Token):
    id = ')'
    regex = re.compile(r'\)')


class LeftBracketToken(Token):
    id = '['
    regex = re.compile(r'\[')


class RightBracketToken(Token):
    id = ']'
    regex = re.compile(r'\]')


class EOFToken(Token):
    id = 'end of file'
    regex = re.compile(r'\0')