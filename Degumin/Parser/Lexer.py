from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, Optional, Type, TypeVar, Union

T = TypeVar("T")

Chunk_Type = Union["LineBreak", "LineComment", "MultiLineComment", "WordStart"]


class CodeChunkVisitor(ABC, Generic[T]):
    @abstractmethod
    def visit_LineBreak(self, line_break: LineBreak) -> T:
        pass

    @abstractmethod
    def visit_LineComment(self, commet: LineComment) -> T:
        pass

    @abstractmethod
    def visit_MultiLineComment(self, comments: MultiLineComment) -> T:
        pass

    @abstractmethod
    def visit_WordStart(self, chunk: WordStart) -> T:
        pass


@dataclass(kw_only=True)
class CodeChunk(ABC):
    line_start: int
    line_end: int

    @abstractmethod
    def traverse(self, visitor: CodeChunkVisitor[T]) -> T:
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
class LineBreak:
    def traverse(self, visitor: CodeChunkVisitor[T]) -> T:
        return visitor.visit_LineBreak(self)


@dataclass
class LineComment(CodeChunk):
    comment: NonLineBreakString

    def traverse(self, visitor: CodeChunkVisitor[T]) -> T:
        return visitor.visit_LineComment(self)


@dataclass
class MultiLineComment(CodeChunk):
    comment: list[NonLineBreakString | LineBreak]
    number_of_hyphens: int

    def traverse(self, visitor: CodeChunkVisitor[T]) -> T:
        return visitor.visit_MultiLineComment(self)


@dataclass
class WordStart(CodeChunk):
    chunk: str

    def traverse(self, visitor: CodeChunkVisitor[T]) -> T:
        return visitor.visit_WordStart(self)


@dataclass
class UnexpectedCharacterAtIndentationZero:
    char: str
    line: int


line_comment_inner = r"--.*"
line_comment_inner_regex = re.compile(line_comment_inner)
line_comment_regex = re.compile(r"\n" + line_comment_inner)
line_break_regex = re.compile(r" *\n")
indented_line_start_regex = re.compile(r"\n[^ \n]")

multi_line_comment_start_inner = r"{-+"
multi_line_comment_start_inner_regex = re.compile(
    multi_line_comment_start_inner
)
multi_line_comment_start = r"\n" + multi_line_comment_start_inner
multi_line_comment_start_regex = re.compile(multi_line_comment_start)


world_start_inner = r"\w(.|\n)*(?=\n\w|\n--|\n\(|\n\{-|)"
world_start_inner_regex = re.compile(world_start_inner)


def match_line_comment_start(
    text: str, line_number: int
) -> Optional[tuple[str, int, LineComment]]:
    match = line_comment_inner_regex.match(text)
    if match is not None:
        chunk_text = text[: match.end()]
        new_line_number = line_number + chunk_text.count("\n")
        # triming the `--`
        non_line_break = NonLineBreakString(chunk_text[2:])
        result = LineComment(
            non_line_break, line_start=new_line_number, line_end=line_number
        )
        text = text[match.end() :]
        return (text, new_line_number, result)
    return None


def match_line_comment(
    text: str, line_number: int
) -> Optional[tuple[str, int, LineComment]]:
    match = line_comment_regex.match(text)
    if match is not None:
        chunk_text = text[: match.end()]
        new_line_number = line_number + chunk_text.count("\n")
        # triming the `\n--`
        non_line_break = NonLineBreakString(chunk_text[3:])
        result = LineComment(
            non_line_break, line_start=new_line_number, line_end=new_line_number
        )
        text = text[match.end() :]
        return (text, new_line_number, result)
    return None


def match_line_break(
    text: str, line_number: int
) -> Optional[tuple[str, int, LineBreak]]:
    match = line_break_regex.match(text)
    if match is not None:
        new_line_number = line_number + 1
        result = LineBreak()
        text = text[match.end() :]
        return (text, new_line_number, result)
    return None


def advance_to_next_contro_point(
    text: str, line_number: int
) -> tuple[str, int]:
    match_result = indented_line_start_regex.search(text)
    if match_result is not None:
        start = text[: match_result.start()]
        break_lines = start.count("\n")
        end = text[match_result.start() :]
        return (end, break_lines + line_number)
    else:
        break_lines = text.count("\n")
        return ("", break_lines + line_number)


def match_multi_line_comment_start(
    text: str, line_number: int
) -> Optional[tuple[str, int, MultiLineComment]]:
    match = multi_line_comment_start_inner_regex.match(text)
    if match is None:
        return None
    number_of_hyphens = match.end() - 1
    repated_hyphens = number_of_hyphens * r"-"
    new_regex = re.compile(
        r"{" + repated_hyphens + r"(.|\n)*\n" + repated_hyphens + r"}"
    )
    full_match = new_regex.match(text)
    if full_match is None:
        # TODO:  modify the signatures of the `match` functions to handle this.
        return None
    # The 1 here is to remove the `\n` in the end `\n---}`
    match_result = text[match.end() : full_match.end() - match.end() - 1]
    line_counter = 0
    result: list[LineBreak | NonLineBreakString] = []
    for item in match_result.split("\n"):
        if item:
            if item.lstrip():
                result.append(NonLineBreakString(item))
            else:
                result.append(LineBreak())
        else:
            result.append(LineBreak())
        line_counter += 1

    text = text[full_match.end() :]
    new_line_number = line_number + line_counter
    return (
        text,
        new_line_number,
        MultiLineComment(
            result,
            number_of_hyphens,
            line_start=line_number,
            line_end=new_line_number,
        ),
    )


def match_multi_line_comment(
    text: str, line_number: int
) -> Optional[tuple[str, int, MultiLineComment]]:
    match = multi_line_comment_start_regex.match(text)
    if match is None:
        return None
    # We matched for "\n{-+", so, we are discarding the `\n`
    return match_multi_line_comment_start(text[1:], line_number + 1)


def match_world_start(
    text: str, line_number: int
) -> Optional[tuple[str, int, WordStart]]:
    match = world_start_inner_regex.match(text)
    if match is None:
        return None
    chunk = text[: match.end()]
    print("Chunk: ", chunk)
    lines = chunk.count("\n")
    new_line_number = lines + line_number
    new_text = text[match.end() :]
    return (
        new_text,
        new_line_number,
        WordStart(chunk, line_start=line_number, line_end=new_line_number),
    )


def split_by_indentation(
    text: str,
) -> tuple[list[Chunk_Type], list[UnexpectedCharacterAtIndentationZero]]:
    """Every time we find text at the begining of a line, we know
    we found a new region of things to parse, this function
    split a text in all of this regions.
    """
    if len(text) == 0:
        return ([], [])

    line_number: int = 0
    out: list[Chunk_Type] = []
    errors: list[UnexpectedCharacterAtIndentationZero] = []
    if text[0] != "\n":
        for f in [
            match_line_comment_start,
            match_multi_line_comment_start,
            match_world_start,
            match_line_break,
        ]:
            match_result = f(text, line_number)
            if match_result is not None:
                new_text, new_line, result = match_result
                text = new_text
                line_number = new_line
                out.append(result)
                break
        if len(out) == 0:
            errors.append(
                UnexpectedCharacterAtIndentationZero(text[0], line_number)
            )
            text, line_number = advance_to_next_contro_point(text, line_number)
    while text:
        found_one = False
        for f in [
            match_line_comment,
            match_multi_line_comment,
            match_line_break,
        ]:
            match_result = f(text, line_number)
            if match_result is not None:
                new_text, new_line, result = match_result
                text = new_text
                line_number = new_line
                out.append(result)
                found_one = True
                break
        if not found_one:
            errors.append(
                UnexpectedCharacterAtIndentationZero(text[0], line_number)
            )
            text, line_number = advance_to_next_contro_point(text, line_number)
    return (out, errors)
