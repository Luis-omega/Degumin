from dataclasses import dataclass
from typing import Iterable, Optional

from Degumin.Common.Error import DeguminError
from Degumin.Parser.Token import Token


class IndenterError(DeguminError):
    pass


@dataclass
class MissIndented(IndenterError):
    token: Token
    expected_indentation_level: int
    maybe_previous_indentation_token: Optional[Token]


def make_token_error_at(token: Token, err: IndenterError):
    pass


def handle_let(
    let: Token,
    tokens: list[Token],
    last_identation_level: int,
    maybe_previous_indentation_token: Optional[Token],
) -> list[Token]:
    if let.column <= last_identation_level:
        raise MissIndented(
            let, last_identation_level, maybe_previous_indentation_token
        )
    if len(tokens) == 0:
        # this is a parsing error, we should just return the let token
        return [let]
    else:
        first_token = tokens[0]
        # We have last_identation_level < let.column
        if first_token.column <= let.column:
            raise MissIndented(first_token, let.column, let)
        else:
            # take tokens until we find another speciall token and delegate the task to them or we found the `in` token.
            pass

    return []


def segment_file(text: str) -> Iterable[Token]:
    pass
