from typing import Generic, NewType, Optional, TypeVar, Union

from lark import Token, Transformer, Tree, v_args

from Degumin.Common.File import Range, mergeRanges, token2Range
from Degumin.Core.Core import (
    Constructor,
    DataType,
    FreeVariable,
    Hole,
    IntValue,
    Module,
    ModuleHeader,
    Term,
    Universe,
    VariableDeclaration,
    VariableDefinition,
)

T = TypeVar("T")
T2 = TypeVar("T2")


@v_args(inline=True)
class ToCore(Transformer):
    def module(
        self,
        header: ModuleHeader,
        *statements: VariableDeclaration[Range]
        | VariableDefinition[Range]
        | DataType[Range],
    ) -> Module[Range]:
        _range = header.info
        for statement in statements:
            new_range = mergeRanges(statement.info, _range)
        return Module(header, list(*statements), new_range)

    def module_level(
        self,
        statement: VariableDeclaration[Range]
        | VariableDefinition[Range]
        | DataType[Range],
    ) -> (
        VariableDeclaration[Range] | VariableDefinition[Range] | DataType[Range]
    ):
        return statement

    def module_header(
        self, module: Token, identifier: Token, where: Token
    ) -> ModuleHeader[Range]:
        return ModuleHeader(identifier.value, token2Range(identifier))

    def variable_declaration(
        self,
        identifier: Token,
        colon: Token,
        term: Term[Range],
        semi_colon: Token,
    ) -> VariableDeclaration[Range]:
        return VariableDeclaration(
            identifier.value, term, token2Range(identifier)
        )

    def variable_definition(
        self,
        identifier: Token,
        equal: Token,
        term: Term[Range],
        semi_colon: Token,
    ) -> VariableDefinition[Range]:
        return VariableDefinition(
            identifier.value, term, token2Range(identifier)
        )

    def data_definition(
        self,
        data: Token,
        identifier: Token,
        colon: Token,
        term: Term[Range],
        equal: Token,
        definitions: list[Constructor[Range]],
        semi_colon: Token,
    ) -> DataType[Range]:
        return DataType(
            identifier.value,
            term,
            definitions,
            mergeRanges(token2Range(data), token2Range(semi_colon)),
        )

    def constructors_definition(
        self, *definitions: Constructor[Range]
    ) -> list[Constructor[Range]]:
        return list(*definitions)

    def constructor_definition(
        self,
        identifier: Token,
        colon: Token,
        term: Term[Range],
        semi_colon: Token,
    ) -> Constructor[Range]:
        return Constructor(
            identifier.value,
            term,
            mergeRanges(token2Range(identifier), token2Range(semi_colon)),
        )

    def value(self, _int: Token) -> IntValue[Range]:
        return IntValue(_int.value, token2Range(_int))

    def basic_type(self, token: Token) -> Universe[Range]:
        # TODO: Replace Universe for "Type" and add "universe polymorphism"
        return Universe(
            int(token.value.removeprefix("Universe")), token2Range(token)
        )

    def hole(self, token: Token) -> Hole[Range]:
        return Hole(token.value.removeprefix("_"), token2Range(token))
