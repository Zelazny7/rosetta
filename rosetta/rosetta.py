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
        self.walk()

    @property
    def indent(self):
        return Operation._indent

    @indent.setter
    def indent(self, value):
        Operation._indent = value

    def walk(self, other=None):
        """Walk Operation and call matching methods in `other` object"""
        klass = type(self).__name__

        # call EnterAndOperation in `other` object if klass is an AndOperation and attribute exists
        fenter = getattr(other, "Enter" + klass, None)
        if fenter is not None:
            fenter(self)

        # Call walk on children if they exist
        for operand in self.operands:
            operand.walk(other)

        # call ExitAndOperation in `other` object if klass is an AndOperation and attribute exists
        fexit = getattr(other, "Exit" + klass, None)
        if fexit is not None:
            fexit(self)

    def __str__(self):
        self.indent += 2
        res = f"\n".join([(" " * self.indent) + str(x) for x in self.operands])
        self.indent -= 2
        return res + "\n" + " " * self.indent + "]"


class EqualOperation(Operation):
    def __init__(self, target: str, value: Any):
        super().__init__()
        self.target = target
        self.value = value

    def __str__(self) -> str:
        return f"{self.target} == {self.value}"


class InOperation(Operation):
    def __init__(self, target: str, value: List[Any]):
        super().__init__()
        self.target = target
        self.value = value

    def __str__(self) -> str:
        return f"{self.target} in ({', '.join([str(x) for x in self.value])})"


class AndOperation(Operation):
    def __init__(self, operands, **kwargs):
        super().__init__(operands, **kwargs)

    def __str__(self):
        return "and [\n" + super().__str__()


class NotOperation(Operation):
    def __init__(self, operands, **kwargs):
        super().__init__(operands, **kwargs)

    def __str__(self):
        return "not [\n" + super().__str__()


class OrOperation(Operation):
    def __init__(self, operands, **kwargs):
        super().__init__(operands, **kwargs)

    def __str__(self):
        return "or [\n" + super().__str__()


class AssignmentOperation(Operation):
    def __init__(self, variable: str, predicate: Dict[str, Any], value: Any):
        super().__init__()
        self.variable = variable
        self.predicate = Operation.from_dict(predicate)
        self.value = value

    def __str__(self):
        return f"({str(self.predicate)}) => {self.variable} = {self.value}"


class IfElseOperation(Operation):
    def __init__(self, operands: List[Dict[str, Any]]):
        super().__init__(operands)

    def __str__(self):
        return f"ifelse [\n{super().__str__()}]"


class VariableTransformation:
    def __init__(self):
        super().__init__()

    def EnterInOperation(self, other: InOperation):
        print("Entered an In Operation")
        print(str(other))

    def EnterAndOperation(self, other: AndOperation):
        print("Entered And")
        # print(str(other))

    def ExitAndOperation(self, other: AndOperation):
        print("Exited And")
        # print(str(other))


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

    # create compound operation from dictionary
    res1 = Operation.from_dict(d)
    print(res1)

    # demonstrate variable walking
    v = VariableTransformation()
    res1.walk(v)

    # reading from json file
    import json

    with open("specs/example02.json", "r") as fin:
        j = json.load(fin)

    res2 = Operation.from_dict(j)
    print(res2)
