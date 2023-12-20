"""
Defines the surface AST called SST (Sugared Syntax Tree)
"""
from __future__ import annotations

import re
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import Generic, Optional, TypeVar, Union, assert_never

# The type for info parameter of the /
Info = TypeVar("Info")

# Generic type variable.
T = TypeVar("T")

# Type variable holding the valid types that forms the SST
SST_Type = Union["SingleIdentifier"]


class MetaVisitor(Generic[Info, T], metaclass=ABCMeta):
    """
    This meta class MUST be updated every time that we
    add a new node to the SST.
    """

    @abstractmethod
    def visit_Identifier(self, identifier: Identifier[Info]) -> T:
        pass


@dataclass(kw_only=True)
class MetaSST(Generic[Info], metaclass=ABCMeta):
    info: Info = field(compare=False)

    @abstractmethod
    def traverse(self, visitor: MetaVisitor[Info, T]) -> T:
        pass


@dataclass
class SingleIdentifier:
    """
    Class that stores a single identifier i.e. a identifier without ".".
    The __init__ method WON'T check for correctness of the identifier, please
    use `make_SingleIdentifier` instead.

    This isn't part of SST and is not registered in the MetaVisitor,
    the reason is that having the input `a.b.c.d` it doesn't really
    makes sense split he information to provide information for
    `a`, `b`, `c` and `d`.
    Instead we only store the info at the level of `a.b.c.d` in Identifier.
    """

    identifier: str


single_identifier_regex = re.compile(r"[a-zA-Z]|[a-zA-Z_][a-zA-Z0-9_']+")


# TODO: replace the return type Optional with a Union including
# error information. is it worth it?
def make_SingleIdentifier(maybe_identifier: str) -> Optional[SingleIdentifier]:
    """
    Creates a valid `SingleIdentifier` or return None if `maybe_identifier`
    is not a proper identifier.
    """
    result = single_identifier_regex.match(maybe_identifier)
    if result is None:
        return None
    if result.endpos == len(maybe_identifier):
        return SingleIdentifier(maybe_identifier)
    return None


@dataclass
class Identifier(MetaSST[Info]):
    """
    This class represent a non empty list of SingleIdentifier[Info].
    The representation of  `A.B.C` is
        - prefix = [SingleIdentifier("A"),SingleIdentifier("B")]
        - suffix = SingleIdentifier("C")
    This class WON'T check the constraints of Identifier, please
    use `make_Identifier` instead of the class __init__ method.
    """

    prefix: list[SingleIdentifier]
    suffix: SingleIdentifier

    def traverse(self, visitor: MetaVisitor[Info, T]) -> T:
        return visitor.visit_Identifier(self)


def make_Identifier(
    maybe_identifier: str, info: Info
) -> Optional[Identifier[Info]]:
    splitted = maybe_identifier.split(".")
    match splitted:
        case []:
            return None
        case [single]:
            maybe_suffix = make_SingleIdentifier(single)
            if maybe_suffix:
                return Identifier([], maybe_suffix, info=info)
            return None

        case [*prefix_elements, suffix]:
            prefix: list[SingleIdentifier] = []
            for maybe_prefix_element in prefix_elements:
                if local_result := make_SingleIdentifier(maybe_prefix_element):
                    prefix.append(local_result)
                else:
                    return None
            maybe_suffix = make_SingleIdentifier(suffix)
            if maybe_suffix:
                return Identifier(prefix, maybe_suffix, info=info)
            return None
        case _:
            # this is unreachable but mypy can't infer it.
            assert_never(splitted)  # type:ignore
