from dataclasses import dataclass
from typing import Optional

from lark import Lark, UnexpectedInput


class ParserStageError:
    pass


# We couldn't open and read the grammar file
class LoadGrammarError(ParserStageError):
    pass


# Lark can't parse the grammar
@dataclass
class LarkLoadError(ParserStageError):
    msg: str


@dataclass
class FileLoadError(ParserStageError):
    info: int


def load_grammar(
    debug: Optional[bool] = None, start_symbols: Optional[list[str]] = ["top"]
) -> LoadGrammarError | LarkLoadError | Lark:
    if debug is None:
        debug = False
    grammarPath = "Degumin/Grammar.lark"
    if start_symbols is None:
        start_symbols = ["top"]
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


def main(test_file_name: Optional[str] = None) -> None:
    lark = load_grammar(False, ["module"])
    if isinstance(lark, LoadGrammarError):
        print("Can't open or read grammar file")
        return None
    elif isinstance(lark, LarkLoadError):
        print("Problem while processing the grammar")
        print(lark.msg)
        return None
    if test_file_name is None:
        test_file_name = "grammar_test"
    try:
        with open(test_file_name, "r") as test_file:
            to_parser = test_file.read()
    except OSError:
        print(f"Can't open test_file {test_file_name}")
        return None
    try:
        result = lark.parse(to_parser)
    except UnexpectedInput as e:
        context = e.get_context(to_parser)
        print(e)
        print(context)
        return None
    print(result.pretty())
    return None


main()
