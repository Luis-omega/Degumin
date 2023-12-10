"""
Simple module to test how to structure the ast tree
"""
from __future__ import annotations

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Generic, Self, TypeVar, Union

T = TypeVar("T")
T2 = TypeVar("T2")


SimpleAST_Type = Union["Int[T]", "Var[T]", "Add[T]"]


class SimpleAST(Generic[T], metaclass=ABCMeta):
    @abstractmethod
    def traverse(self, visitor: SimpleASTVisitor[T, T2]) -> T2:
        pass


@dataclass
class Int(SimpleAST[T]):
    value: int
    info: T

    def traverse(self: Self, visitor: SimpleASTVisitor[T, T2]) -> T2:
        return visitor.visit_int(self)


@dataclass
class Var(SimpleAST[T]):
    value: str
    info: T

    def traverse(self, visitor: SimpleASTVisitor[T, T2]) -> T2:
        return visitor.visit_var(self)


@dataclass
class Add(SimpleAST[T]):
    left: SimpleAST_Type[T]
    right: SimpleAST_Type[T]
    info: T

    def traverse(self, visitor: SimpleASTVisitor[T, T2]) -> T2:
        return visitor.visit_add(self)


class SimpleASTVisitor(Generic[T, T2], metaclass=ABCMeta):
    @abstractmethod
    def visit_int(self, value: Int[T]) -> T2:
        pass

    @abstractmethod
    def visit_var(self, value: Var[T]) -> T2:
        pass

    @abstractmethod
    def visit_add(self, value: Add[T]) -> T2:
        pass


class InterpreterVisitor(SimpleASTVisitor[T, int]):
    def visit_int(self, value: Int[T]) -> int:
        return value.value

    def visit_var(self, value: Var[T]) -> int:
        return 1

    def visit_add(self, value: Add[T]) -> int:
        left = value.left.traverse(self)
        right = value.right.traverse(self)
        return left + right


class EasyPrintVisitor(SimpleASTVisitor[T, str]):
    def visit_int(self, value: Int[T]) -> str:
        return str(value.value)

    def visit_var(self, value: Var[T]) -> str:
        return value.value

    def visit_add(self, value: Add[T]) -> str:
        left = value.left.traverse(self)
        right = value.right.traverse(self)
        return f"{left} + {right}"


@dataclass(kw_only=True)
class Some1(metaclass=ABCMeta):
    some1: int


@dataclass
class Some2(Some1):
    some2: int


def interpreter(ast: SimpleAST[T]) -> int:
    return ast.traverse(InterpreterVisitor())


def pretty(ast: SimpleAST[T]) -> str:
    return ast.traverse(EasyPrintVisitor())


def test_simple_test():
    assert 2 == interpreter(Add(Int(1, None), Var("hi", None), None))
    assert "1 + hi" == pretty(Add(Int(1, None), Var("hi", None), None))


def test_some():
    assert 2 == Some2(2, some1=1)


test_simple_test()
