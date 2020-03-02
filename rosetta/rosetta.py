from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Type, cast

class Operation:
    registry: Dict[str, Type[Operation]] = {}
    _indent: int = 0

    @staticmethod
    def register_operation(op: str, klass: Type[Operation]):
        Operation.registry[op] = klass

    @staticmethod
    def from_dict(x: Dict[str, Any]) -> Operation:
        klass = Operation.registry.get(x["op"])
        if klass is None:
            raise ValueError(f"Operation: {x['op']} not registered.")
        else:
            del x["op"]
            return klass(**x)

    def __init__(self, operands=None, **kwargs):
        super().__init__()
        if operands is not None:
            self.operands = [Operation.from_dict(d) for d in operands]
        else:
            self.operands = []


class EqualOperation(Operation):
    def __init__(self, target: str, value: Any):
        super().__init__()
        self.target = target
        self.value = value


class InOperation(Operation):
    def __init__(self, target: str, value: List[Any]):
        super().__init__()
        self.target = target
        self.value = value


class AndOperation(Operation):
    def __init__(self, operands, **kwargs):
        super().__init__(operands, **kwargs)


class NotOperation(Operation):
    def __init__(self, operands, **kwargs):
        super().__init__(operands, **kwargs)


class OrOperation(Operation):
    def __init__(self, operands, **kwargs):
        super().__init__(operands, **kwargs)


class AssignmentOperation(Operation):
    def __init__(self, variable: str, predicate: Dict[str, Any], value: Any):
        super().__init__()
        self.variable = variable
        self.predicate = Operation.from_dict(predicate)
        self.value = value


class IfOperation(Operation):
    def __init__(self, operands: List[Dict[str, Any]], variable: str, value: Any):
        print(operands)
        super().__init__(operands)


class IfElseOperation(Operation):
    def __init__(self, operands: List[Dict[str, Any]]):
        super().__init__(operands)


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


if __name__ == "__main__":
    d = {
        "op": "and",
        "operands": [
            {"op": "eq", "target": "mpg", "value": 25},
            {
                "op": "not",
                "operands": [
                    {
                        "op": "or",
                        "operands": [
                            {"op": "eq", "target": "disp", "value": 10},
                            {"op": "in", "target": "cyl", "value": [2, 4, 6, 8]},
                        ],
                    }
                ],
            },
        ],
    }

    # register operations with factory
    Operation.register_operation("and", AndOperation)
    Operation.register_operation("eq", EqualOperation)
    Operation.register_operation("not", NotOperation)
    Operation.register_operation("or", OrOperation)
    Operation.register_operation("in", InOperation)
    Operation.register_operation("assign", AssignmentOperation)
    Operation.register_operation("ifelse", IfElseOperation)
    Operation.register_operation("if", IfOperation)

    # create compound operation from dictionary
    res1 = Operation.from_dict(d)
    # print(res1)

    # demonstrate variable walking
    v = PandasVisitor(df="df", variable="var1")

    v.visit(res1)
    # res1.walk(v)

    # v2 = StringTransformer()
    # res1.walk(v2)

    # reading from json file
    # import json

    # with open("specs\\example02.json", "r") as fin:
    #     j = json.load(fin)

    # res2 = Operation.from_dict(j)
    # res2.walk(v2)
    # print(res2)
