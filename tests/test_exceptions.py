from mel.parsing import Parser
from mel.lexing import TokenStream
from mel.exceptions import ParsingError
from mel.exceptions.formatting import ErrorFormatter


def parse(text):
    stream = TokenStream(text)
    return Parser(stream).parse()


def test_error_line_and_column():
    try:
        parse("33 #")
    except ParsingError as error:
        assert error.line == 0
        assert error.column == 3


def test_error_text_and_index():
    text = "name !!"
    try:
        parse(text)
    except ParsingError as error:
        assert error.text == text
        assert error.index == 5


def test_error_message_header():
    header = "Error at line 2, column 1."
    try:
        parse("42\n%\n'string'")
    except ParsingError as error:
        message = ErrorFormatter(error).format()
        assert header in message


def test_error_message_snippet():
    snippet = "\n".join([
        "1 | 42",
        "2 | %",
        "----^",
        "3 | 'string'"
    ])
    try:
        parse("42\n%\n'string'")
    except ParsingError as error:
        message = ErrorFormatter(error).format()
        assert snippet in message
