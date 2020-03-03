from __future__ import annotations
from rosetta.operations import *


def invoke(object: BaseVisitor, prefix: str, op: Operation) -> None:
    """Check if object has `prefix` + `type(op).__name__` as an attribute and call"""
    klass = type(op).__name__
    func = getattr(object, prefix + klass, None)
    if func is not None:
        func(op)


class BaseVisitor(ABC):
    def __init__(self, indent_size=2):
        super().__init__()
        self._indent = 0
        self.indent_size = indent_size

    @property
    def s(self) -> str:
        """Create spaces for formatting output"""
        return " " * self._indent

    def visit(self, op: Operation):
        """Walk Operation and call matching methods in `other` object"""

        invoke(self, "Enter", op)

        # Call walk on children if they exist
        self._indent += self.indent_size
        for i, operand in enumerate(op.operands):
            self.visit(operand)

            if i < len(op.operands) - 1:
                invoke(self, "While", op)

            if i == len(op.operands):
                invoke(self, "Last", op)

        self._indent -= self.indent_size

        invoke(self, "Exit", op)


class StringVisitor(BaseVisitor):
    def EnterEqualOperation(self, other: EqualOperation):
        print(f"{other.target} == {other.value}", end="")

    def EnterInOperation(self, other: InOperation):
        print(f"{other.target} in ({', '.join([str(x) for x in other.value])})", end="")

    def WhileIfElseOperation(self, other: IfElseOperation):
        print(f"\nelse ", end="")

    def EnterIfOperation(self, other: IfOperation):
        print(f"if (", end="")

    def ExitIfOperation(self, other: IfOperation):
        print(f"):", end="")


class PandasVisitor(BaseVisitor):
    def __init__(self, df: str, variable: str):
        super().__init__()
        self.variable = variable
        self.df = df

    def EnterInOperation(self, other: InOperation):
        res = f'{self.s}({self.df}["{other.target}"].isin({str(other.value)}))'
        print(res, end="")

    def EnterAndOperation(self, other: AndOperation):
        print(self.s + "(", end="")

    def WhileAndOperation(self, other: AndOperation):
        print(" &")

    def ExitAndOperation(self, other: AndOperation):
        print(")", end="")

    def EnterEqualOperation(self, other: EqualOperation):
        print(f'({self.df}["{other.target}"] == {other.value})', end="")

    def EnterNotOperation(self, other: NotOperation):
        print(f"{self.s}~", end="")

    def EnterOrOperation(self, other: OrOperation):
        print("(", end="")

    def WhileOrOperation(self, other: OrOperation):
        print(" |")

    def ExitOrOperation(self, other: OrOperation):
        print(")", end="")
