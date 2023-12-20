import pytest

from Degumin.Parser.Lexer import (
    LineBreak,
    LineComment,
    MultiLineComment,
    NonLineBreakString,
    WordStart,
    split_by_indentation,
)


@pytest.mark.parametrize(
    "text,expected",
    [
        (
            "-- hi world",
            LineComment(
                NonLineBreakString(" hi world"), line_start=0, line_end=0
            ),
        ),
        (
            "-- something\nasdf\nas\n",
            LineComment(
                NonLineBreakString(" something"), line_start=0, line_end=0
            ),
        ),
    ],
)
def test_single_line_comment_at_start(text, expected):
    result, errors = split_by_indentation(text)
    assert result[0] == expected
    assert errors == []


@pytest.mark.parametrize(
    "text,expected,expected_index",
    [
        (
            "\n-- hi world",
            LineComment(
                NonLineBreakString(" hi world"), line_start=1, line_end=1
            ),
            0,
        ),
        (
            "\n\n\n-- something\nasdf\nas\n",
            LineComment(
                NonLineBreakString(" something"), line_start=3, line_end=3
            ),
            2,
        ),
    ],
)
def test_single_line_comment(
    text: str, expected: LineComment, expected_index: int
):
    result, errors = split_by_indentation(text)
    assert result[expected_index] == expected
    assert errors == []


@pytest.mark.parametrize(
    "text,expected",
    [
        (
            "{-some text\n-}",
            MultiLineComment(
                [NonLineBreakString("some text")], 1, line_start=0, line_end=1
            ),
        ),
        (
            "{-some text\n\n-}",
            MultiLineComment(
                [
                    NonLineBreakString("some text"),
                    LineBreak(),
                ],
                1,
                line_start=0,
                line_end=2,
            ),
        ),
        (
            "{-some \n text\n-}",
            MultiLineComment(
                [
                    NonLineBreakString("some "),
                    NonLineBreakString(" text"),
                ],
                1,
                line_start=0,
                line_end=2,
            ),
        ),
        (
            "{---- some text\n----}",
            MultiLineComment(
                [NonLineBreakString(" some text")], 4, line_start=0, line_end=1
            ),
        ),
        (
            "{---- some text\n----}\n\n--another\n-- comments",
            MultiLineComment(
                [NonLineBreakString(" some text")], 4, line_start=0, line_end=1
            ),
        ),
        (
            "{------ some\ntext\nis\n\n\ngood\n------}",
            MultiLineComment(
                [
                    NonLineBreakString(" some"),
                    NonLineBreakString("text"),
                    NonLineBreakString("is"),
                    LineBreak(),
                    LineBreak(),
                    NonLineBreakString("good"),
                ],
                6,
                line_start=0,
                line_end=6,
            ),
        ),
    ],
)
def test_multiline_comment_start(text: str, expected: MultiLineComment):
    result, errors = split_by_indentation(text)
    assert result[0] == expected
    assert errors == []


@pytest.mark.parametrize(
    "text,expected,expected_index",
    [
        (
            "\n\n\n{----- some\ntext\nis\n\n\ngood\n-----}",
            MultiLineComment(
                [
                    NonLineBreakString(" some"),
                    NonLineBreakString("text"),
                    NonLineBreakString("is"),
                    LineBreak(),
                    LineBreak(),
                    NonLineBreakString("good"),
                ],
                5,
                line_start=3,
                line_end=9,
            ),
            2,
        )
    ],
)
def test_multiline_comment(
    text: str, expected: MultiLineComment, expected_index: int
):
    result, errors = split_by_indentation(text)
    print(result)
    assert result[expected_index] == expected
    assert errors == []


@pytest.mark.parametrize(
    "text,expected",
    [
        ("some worlds", WordStart("some worlds", line_start=0, line_end=0)),
        (
            "some\n\n worlds",
            WordStart("some\n\n worlds", line_start=0, line_end=2),
        ),
        ("some worlds\n(", WordStart("some worlds", line_start=0, line_end=0)),
        (
            "some worlds\n{- -}",
            WordStart("some worlds", line_start=0, line_end=0),
        ),
        ("some worlds\nas", WordStart("some worlds", line_start=0, line_end=0)),
        ("some worlds\n--", WordStart("some worlds", line_start=0, line_end=0)),
        (
            "some worlds\n{",
            WordStart("some worlds\n{", line_start=0, line_end=1),
        ),
        (
            "some worlds\n-",
            WordStart("some worlds\n-", line_start=0, line_end=1),
        ),
    ],
)
def test_world_start(text: str, expected: WordStart):
    result, errors = split_by_indentation(text)
    print(result)
    assert result[0] == expected
    assert errors == []


@pytest.mark.skip
def test_lexer():
    test_input = """
module a where

-- this is a comment1

{- this is
another
comment2
 -}

hi = "hi"

bye a b c = 
 asdf
"""
    out = split_by_indentation(test_input)
    expected = [
        "module a where\n",
        "-- this is a comment1\n",
        "{- this is\n another\ncomment2\n -}\n",
        'hi = "hi"\n',
        "bye a bc =\n asdf\n",
    ]
    assert expected == out
