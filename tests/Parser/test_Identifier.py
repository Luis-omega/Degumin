import pytest

from Degumin.CST.CST import (
    Identifier,
    SingleIdentifier,
    make_Identifier,
    make_SingleIdentifier,
    single_identifier_regex,
)


@pytest.mark.parametrize(
    "single_identifier",
    ["a", "bc", "a_", "a'", "a_b", "a'_b'c", "_'", "asf90_er3'3423w"],
)
def test_identifier_no_prefix(single_identifier):
    result = make_SingleIdentifier(single_identifier)
    expected = SingleIdentifier(single_identifier)
    assert result == expected


@pytest.mark.parametrize(
    "single_no_identifier",
    ["_", "'", ".", ":", "?", "'asd", ".asf", "'_", "9'_asdf", "2_,3er"],
)
def test_negative_identifier_no_prefix(single_no_identifier):
    result = make_SingleIdentifier(single_no_identifier)
    assert result is None


@pytest.mark.parametrize(
    "prefix,suffix",
    [
        (["a", "b", "c"], "a"),
        (["a"], "bc"),
        ([], "a_"),
        (["Data", "Control", "Monad'", "Extrangenous"], "a'"),
        (["asfd"], "a_b"),
        ([], "a'_b'c"),
        (["AS", "d_er", "e"], "_'"),
        (["Identity"], "asf90_er3'3423w"),
    ],
)
def test_identifier(prefix: list[str], suffix: str):
    prefix_joined = ".".join(prefix)
    result = make_Identifier(
        prefix_joined + "." + suffix if prefix_joined else suffix, info=None
    )
    expected = Identifier(
        [SingleIdentifier(i) for i in prefix],
        SingleIdentifier(suffix),
        info=None,
    )
    assert result == expected


@pytest.mark.parametrize(
    "no_identifier",
    [
        "_",
        "'",
        ".",
        ":",
        "?",
        "'asd",
        ".asf",
        "'_",
        "9'_asdf",
        "2_,3er" "a.b.c:asf.w",
        "c.ef.efER.wer'.?asf",
        "c.ef.efER.wer'.?asf.wer9wer_WER",
    ],
)
def test_negative_identifier(no_identifier):
    result = make_Identifier(no_identifier, info=None)
    assert result is None


# TODO:
# def test_print_single_identifier():
#     result = SingleIdentifier("ab").traverse(Pretty)
#     expected = "ab"
#     assert result == expected
