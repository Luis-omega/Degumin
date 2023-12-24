from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, Optional, Type, TypeVar, Union

from Degumin.Common.Error import DeguminError
from Degumin.Common.File import Range

T = TypeVar("T")

Chunk_Type = Union["LineBreak", "LineComment", "MultiLineComment", "WordStart"]


class SegmenterError(ABC, DeguminError):
    @abstractmethod
    def visit(self, visitor: SegmenterErrorVisitor[T]) -> T:
        pass


class SegmenterErrorVisitor(ABC, Generic[T]):
    @abstractmethod
    def visit_unexpected_character(
        self, e: UnexpectedCharacterAtIndentationZero
    ) -> T:
        pass

    @abstractmethod
    def visit_missed_block_coment_close(self, e: MissedBlockCommentClose) -> T:
        pass


@dataclass
class UnexpectedCharacterAtIndentationZero(SegmenterError):
    char: str
    line: int

    def visit(self, visitor: SegmenterErrorVisitor[T]) -> T:
        return visitor.visit_unexpected_character(self)


@dataclass
class MissedBlockCommentClose(SegmenterError):
    line: int
    column: int
    position: int

    def visit(self, visitor: SegmenterErrorVisitor[T]) -> T:
        return visitor.visit_missed_block_coment_close(self)


@dataclass
class State:
    text: str
    position: int
    line: int
    column: int

    def advance_assuming_text(self, text: str) -> Range:
        old_position = self.position
        old_line = self.line
        old_column = self.column
        self.position = old_position + len(text)
        self.line = old_line + text.count("\n")
        self.column = len(text[::-1].split("\n", maxsplit=1)[0])
        return Range(
            line_start=old_line,
            line_end=self.line,
            column_start=old_column,
            column_end=self.column,
            position_start=old_position,
            position_end=self.position,
        )

    def match(self, pattern: re.Pattern) -> Optional[tuple[str, Range]]:
        result = pattern.match(self.text[self.position :])
        if result is None:
            return None
        matched = self.text[self.position : self.position + result.end()]
        _range = self.advance_assuming_text(matched)
        return (matched, _range)

    def start_match(self, pattern=str) -> Optional[Range]:
        """
        Pattern shouldn't contain "\n"
        """
        if pattern.count("\n") > 0:
            return None
        text = self.get_remaining_text()
        real_pattern = r"\n" + pattern
        print(
            "starts with",
            real_pattern.replace("\n", "\\n"),
            "?",
            text.replace("\n", "\\n"),
            text.startswith(real_pattern),
        )
        if re.match(real_pattern, (text)):
            print("matched")
            _range = self.advance_assuming_text("\n")
            return _range
        return None

    def get_remaining_text(self) -> str:
        return self.text[self.position :]

    def advance_to_next_control_point(self) -> None:
        text = self.get_remaining_text()
        match_result = indented_line_start_regex.search(text)
        print("SEARCH result = ", match_result)
        if match_result is None:
            self.advance_assuming_text(text)
        else:
            new_text = text[match_result.end() :]
            self.advance_assuming_text(new_text)

    def is_at_end(self) -> bool:
        return len(self.text) <= self.position


class CodeChunkVisitor(ABC, Generic[T]):
    @abstractmethod
    def visit_LineBreak(self, line_break: LineBreak) -> T:
        pass

    @abstractmethod
    def visit_LineComment(self, comment: LineComment) -> T:
        pass

    @abstractmethod
    def visit_MultiLineComment(self, comments: MultiLineComment) -> T:
        pass

    @abstractmethod
    def visit_WordStart(self, chunk: WordStart) -> T:
        pass


@dataclass(kw_only=True)
class CodeChunk(ABC):
    _range: Range

    @abstractmethod
    def visit(self, visitor: CodeChunkVisitor[T]) -> T:
        pass


NonLineBreakString_Type = TypeVar(
    "NonLineBreakString_Type", bound="NonLineBreakString"
)


@dataclass
class NonLineBreakString:
    value: str

    @classmethod
    def make_NonLineBreakString(
        cls: Type[NonLineBreakString_Type], value: str
    ) -> Optional[NonLineBreakString_Type]:
        if "\n" in value:
            return None
        else:
            return cls(value)


@dataclass
class LineBreak(CodeChunk):
    def visit(self, visitor: CodeChunkVisitor[T]) -> T:
        return visitor.visit_LineBreak(self)


@dataclass
class LineComment(CodeChunk):
    comment: NonLineBreakString

    def visit(self, visitor: CodeChunkVisitor[T]) -> T:
        return visitor.visit_LineComment(self)


@dataclass
class MultiLineComment(CodeChunk):
    comment: list[NonLineBreakString | LineBreak]
    number_of_hyphens: int

    def visit(self, visitor: CodeChunkVisitor[T]) -> T:
        return visitor.visit_MultiLineComment(self)


@dataclass
class WordStart(CodeChunk):
    chunk: str

    def visit(self, visitor: CodeChunkVisitor[T]) -> T:
        return visitor.visit_WordStart(self)


line_comment_inner = r"--.*"
line_comment_inner_regex = re.compile(line_comment_inner)
line_comment_regex = re.compile(r"\n" + line_comment_inner)
line_break_regex = re.compile(r" *\n *")
indented_line_start_regex = re.compile(r"\n[^ \n]")

multi_line_comment_start_inner = r"{-+"
multi_line_comment_start_inner_regex = re.compile(
    multi_line_comment_start_inner
)
multi_line_comment_start = r"\n" + multi_line_comment_start_inner
multi_line_comment_start_regex = re.compile(multi_line_comment_start)


world_start_inner = r"\w(.|\n)*(?=\n\w|\n--|\n\(|\n\{-|$)"
world_start_inner_regex = re.compile(world_start_inner)


def match_line_comment_inner(state: State) -> Optional[LineComment]:
    matched = state.match(line_comment_inner_regex)
    if matched is None:
        return None
    text, _range = matched
    # we must trim the -- of the comment
    return LineComment(NonLineBreakString(text[2:]), _range=_range)


def match_line_comment(state: State) -> Optional[LineComment]:
    start_range = state.start_match("--")
    if start_range is None:
        return None
    return match_line_comment_inner(state)


def match_line_break(state: State) -> Optional[LineBreak]:
    matched = state.match(line_break_regex)
    if matched is None:
        return None
    _, _range = matched
    return LineBreak(_range=_range)


def match_multi_line_comment_inner(
    state: State,
) -> Optional[MultiLineComment | MissedBlockCommentClose]:
    text = state.get_remaining_text()
    matched = re.match("{-+", text)
    if matched is None:
        return None
    number_of_hyphens = matched.end() - 1
    repated_hyphens = number_of_hyphens * r"-"
    new_regex = re.compile(
        r"{" + repated_hyphens + r"(.|\n)*\n" + repated_hyphens + r"}"
    )
    real_matched = state.match(new_regex)
    if real_matched is None:
        return MissedBlockCommentClose(state.line, state.column, state.position)
    match_result, match_range = real_matched
    line_counter = 0
    result: list[LineBreak | NonLineBreakString] = []
    for item in match_result[matched.end() : -matched.end() - 1].split("\n"):
        if item:
            if item.lstrip():
                result.append(NonLineBreakString(item.rstrip()))
            else:
                # TODO: put the real info here
                result.append(LineBreak(_range=Range(0, 0, 0, 0, 0, 0)))
        else:
            # TODO: put the real info here
            result.append(LineBreak(_range=Range(0, 0, 0, 0, 0, 0)))
        line_counter += 1
    return MultiLineComment(result, number_of_hyphens, _range=match_range)


def match_multi_line_comment(
    state: State,
) -> Optional[MultiLineComment | MissedBlockCommentClose]:
    start_range = state.start_match("{-+")
    if start_range is None:
        return None
    return match_multi_line_comment_inner(state)


def match_word_inner(state: State) -> Optional[WordStart]:
    matched = state.match(world_start_inner_regex)
    if matched is None:
        return None
    text, _range = matched
    return WordStart(text, _range=_range)


def match_word(state: State) -> Optional[WordStart]:
    start_range = state.start_match(r"\w")
    if start_range is None:
        return None
    return match_word_inner(state)


def split_by_indentation(
    text: str,
) -> tuple[list[Chunk_Type], list[SegmenterError]]:
    """Every time we find text at the begining of a line, we know
    we found a new region of things to parse, this function
    split a text in all of this regions.
    """
    if len(text) == 0:
        return ([], [])
    state = State(text, 0, 0, 0)

    out: list[Chunk_Type] = []
    errors: list[SegmenterError] = []
    if text[0] != "\n":
        for f in [
            match_line_comment_inner,
            match_word_inner,
            match_multi_line_comment_inner,
            match_line_break,
        ]:
            match_result = f(state)
            if match_result is not None:
                if isinstance(match_result, CodeChunk):
                    print(
                        "FOUND: ",
                        match_result,
                        f,
                        state.get_remaining_text().replace("\n", "\\n"),
                    )
                    out.append(match_result)
                    break
                else:
                    print("matched {- but not matched -}")
                    errors.append(match_result)
                    state.advance_to_next_control_point()
        if len(out) == 0:
            errors.append(
                UnexpectedCharacterAtIndentationZero(state.text[0], state.line)
            )
            state.advance_to_next_control_point()
    while not state.is_at_end():
        found_one = False
        for f in [
            match_line_comment,
            match_word,
            match_multi_line_comment,
            match_line_break,
        ]:
            match_result = f(state)
            if match_result is not None:
                if isinstance(match_result, CodeChunk):
                    print(
                        "FOUND: ",
                        match_result,
                        f,
                        state.get_remaining_text().replace("\n", "\\n"),
                    )
                    if not isinstance(match_result, LineBreak):
                        r = match_result._range
                        _range = Range(
                            r.line_end,
                            r.line_end,
                            0,
                            0,
                            r.position_end,
                            r.position_end,
                        )
                        new_line_break = LineBreak(_range=_range)
                        # print("injecting line break")
                        out.append(new_line_break)
                    out.append(match_result)
                    found_one = True
                    break
                else:
                    _range = Range(
                        match_result.line,
                        match_result.line,
                        0,
                        0,
                        match_result.position,
                        match_result.position,
                    )
                    new_line_break = LineBreak(_range=_range)
                    # print("injecting line break")
                    out.append(new_line_break)
                    errors.append(match_result)
                    state.advance_to_next_control_point()
                    found_one = True
                    break

        if not found_one:
            print("NOT FOUND, advancing")
            errors.append(
                UnexpectedCharacterAtIndentationZero(state.text[0], state.line)
            )
            state.advance_to_next_control_point()
    return (out, errors)
