from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from lark import (
    GrammarError,
    Lark,
    Tree,
    UnexpectedCharacters,
    UnexpectedInput,
    UnexpectedToken,
)

from Degumin.Common.Error import DeguminError
from Degumin.Common.File import FileInfo
from Degumin.Parser.Token import Token


class ParseError(DeguminError):
    pass


# We couldn't open and read the grammar file
class LoadGrammarError(ParseError):
    pass


# Lark can't parse the grammar
@dataclass
class LarkLoadError(ParseError):
    msg: str


@dataclass
class FileLoadError(ParseError):
    info: FileInfo


def load_grammar(
    debug: Optional[bool] = None, start_symbols: Optional[list[str]] = ["start"]
) -> LoadGrammarError | LarkLoadError | Lark:
    if debug is None:
        debug = False
    grammarPath = "Degumin/Grammar.lark"
    if start_symbols is None:
        start_symbols = ["start"]
    try:
        with open(grammarPath, "r") as grammarFile:
            grammar = grammarFile.read()
            try:
                parser = Lark(
                    grammar,
                    start=start_symbols,
                    debug=debug,
                    cache=None,
                    propagate_positions=False,
                    maybe_placeholders=True,
                    keep_all_tokens=True,
                    parser="lalr",
                    lexer="basic",
                    # postlex=Indenter(),
                )
            except Exception as e:
                return LarkLoadError(str(e))
    except OSError:
        return LoadGrammarError()
    return parser


def parse_string(
    lark: Lark, info: FileInfo, text: str
) -> list[Tree[Token] | ParseError]:
    results: list[Tree[Token] | ParseError] = []
    # TODO: refactor this to return the list
    try:
        result = lark.parse(text)
        return result  # type:ignore
    except UnexpectedInput as uinput:
        return make_parse_error_from_lark_error(uinput, text, info)


def parse_file(
    path: Path, lark: Lark, debug: bool
) -> FileLoadError | tuple[FileInfo, ParseError | Tree[Token]]:
    info = FileInfo(path.name, path)
    try:
        with open(path, "r") as file:
            content = file.read()
            maybe_tree = parse_string(lark, info, content)
            return (info, maybe_tree)
    except OSError:
        return FileLoadError(info)


def make_parse_error_from_lark_error(
    err: UnexpectedInput, text: str, info: FileInfo
) -> ParseError:
    pass
