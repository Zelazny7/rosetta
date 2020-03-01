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

    def __init__(self, **kwargs):
        super().__init__()

    @property
    def indent(self):
        return Operation._indent

    @indent.setter
    def indent(self, value):
        Operation._indent = value


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


class MultiOperation(Operation, ABC):
    """MultiOperations combine collections of SingleOperations"""

    def __init__(self, operands: List[Dict[str, Any]], **kwargs):
        super().__init__(**kwargs)
        self.operands = [Operation.from_dict(d) for d in operands]

    def __str__(self):
        self.indent += 2
        res = f"\n".join([(" " * self.indent) + str(x) for x in self.operands])
        self.indent -= 2
        return res + "\n" + " " * self.indent + "]"


class AndOperation(MultiOperation):
    def __init__(self, operands, **kwargs):
        super().__init__(operands, **kwargs)

    def __str__(self):
        return "and [\n" + super().__str__()


class NotOperation(MultiOperation):
    def __init__(self, operands, **kwargs):
        super().__init__(operands, **kwargs)

    def __str__(self):
        return "not [\n" + super().__str__()


class OrOperation(MultiOperation):
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


class IfElseOperation(MultiOperation):
    def __init__(self, operands: List[Dict[str, Any]]):
        super().__init__(operands)

    def __str__(self):
        return f"ifelse [\n{super().__str__()}]"


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

    Operation.register_operation("and", AndOperation)
    Operation.register_operation("eq", EqualOperation)
    Operation.register_operation("not", NotOperation)
    Operation.register_operation("or", OrOperation)
    Operation.register_operation("in", InOperation)

    Operation.register_operation("assign", AssignmentOperation)
    Operation.register_operation("ifelse", IfElseOperation)

    res1 = Operation.from_dict(d)
    print(res1)

    import json

    with open("specs/example02.json", "r") as fin:
        j = json.load(fin)

    res2 = Operation.from_dict(j)
    print(res2)

    import inspect

    # print(inspect.getmembers(AssignmentOperation))

    print(AssignmentOperation.__dict__)
