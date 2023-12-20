from dataclasses import dataclass
from typing import Generic, NewType, Optional, TypeVar, Union

T = TypeVar("T")

Term = Union[
    "IntValue"[T],
    "Hole"[T],
    "Universe"[T],
    "Variable"[T],
    "FreeVariable"[T],
    "Abstraction"[T],
    "Forall"[T],
    "Application"[T],
    "Let"[T],
    "Constructor"[T],
    "Case"[T],
    "Annotation"[T],
]

Identifier = NewType("Identifier", str)


@dataclass
class IntValue(Generic[T]):
    value: int
    info: T


@dataclass
class Hole(Generic[T]):
    name: Identifier
    info: T


@dataclass
class Universe(Generic[T]):
    value: int
    info: T


@dataclass
class Variable(Generic[T]):
    number: int
    original_name: Identifier
    info: T


@dataclass
class FreeVariable(Generic[T]):
    name: Identifier
    info: T


@dataclass
class Abstraction(Generic[T]):
    original_arguments: list["DefaultCase"[T] | FreeVariable[T] | Hole[T]]
    term: Term[T]
    info: T


@dataclass
class Forall(Generic[T]):
    arguments: list[tuple[Term[T]]]
    term: Term[T]
    info: T


@dataclass
class Application(Generic[T]):
    left: Term[T]
    right: Term[T]
    info: T


@dataclass
class Let(Generic[T]):
    isRecursive: bool
    definitions: dict[Identifier, Term[T]]
    term: Term[T]
    info: T


@dataclass
class Constructor(Generic[T]):
    name: Identifier
    arguments: Term[T]
    info: T


# This collection of Match is only to define the variants of "case" expression


@dataclass
class MatchLiteralInt(Generic[T]):
    literal: int
    info: T


@dataclass
class MatchLiteralBool(Generic[T]):
    literal: bool
    info: T


@dataclass
class DefaultCase(Generic[T]):
    info: T


@dataclass
class MatchVariable(Generic[T]):
    name: Identifier
    info: T


@dataclass
class MatchConstructor(Generic[T]):
    name: Identifier
    matches: list[
        MatchLiteralInt[T]
        | MatchLiteralBool[T]
        | DefaultCase[T]
        | MatchVariable[T]
        | Hole[T]
    ]
    info: T


@dataclass
class Alternative(Generic[T]):
    case: MatchLiteralBool[T] | MatchLiteralInt[T] | DefaultCase[
        T
    ] | MatchVariable[T] | MatchConstructor[T] | Hole[T]
    value: Term[T]
    info: T


@dataclass
class Case(Generic[T]):
    expression: Term[T]
    alternatives: list[Alternative]
    info: T


@dataclass
class Annotation(Generic[T]):
    expression: Term[T]
    annotation: Term[T]
    info: T


@dataclass
class VariableDeclaration(Generic[T]):
    name: Identifier
    declaration: Term[T]
    info: T


@dataclass
class VariableDefinition(Generic[T]):
    name: Identifier
    definition: Term[T]
    info: T


@dataclass
class DataType(Generic[T]):
    name: Identifier
    argument: Term[T]
    constructors: list[Constructor]
    info: T


@dataclass
class ModuleHeader(Generic[T]):
    name: Identifier
    info: T


@dataclass
class Module(Generic[T]):
    header: ModuleHeader
    statements: list[
        VariableDeclaration[T] | VariableDefinition[T] | DataType[T]
    ]
    info: T


@dataclass
class Context(Generic[T]):
    parent: "Context"
    local: dict[Identifier | int, tuple[Term[T], Term[T]]]

    def lookup(
        self, name: Identifier | int
    ) -> Optional[tuple[Term[T], Term[T]]]:
        result1 = self.local.get(name, None)
        if result1 is None:
            return self.parent.lookup(name)
        else:
            return result1

    def extend(
        self, new: dict[Identifier | int, tuple[Term[T], Term[T]]]
    ) -> "Context":
        return Context(self, new)
