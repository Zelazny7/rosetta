from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Type, cast

# TODO: Create StdoutTransformer instead of __str__ methods for each operation

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
        # self.walk()

    @property
    def indent(self):
        return Operation._indent

    @indent.setter
    def indent(self, value):
        Operation._indent = value

    def walk(self, other: BaseTransformer):
        """Walk Operation and call matching methods in `other` object"""
        klass = type(self).__name__

        # call EnterAndOperation in `other` object if klass is an AndOperation and attribute exists
        fenter = getattr(other, "Enter" + klass, None)
        if fenter is not None:
            fenter(self)

        # Call walk on children if they exist
        other.indent += 2
        for i, operand in enumerate(self.operands):
            operand.walk(other)

            if i < len(self.operands):
                fwhile = getattr(other, "While" + klass, None)
                if fwhile is not None:
                    fwhile(self)
        
        other.indent -= 2

        # call ExitAndOperation in `other` object if klass is an AndOperation and attribute exists
        fexit = getattr(other, "Exit" + klass, None)
        if fexit is not None:
            fexit(self)

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

    # def __str__(self):
    #     return "and [\n" + super().__str__()


class NotOperation(Operation):
    def __init__(self, operands, **kwargs):
        super().__init__(operands, **kwargs)

    # def __str__(self):
    #     return "not [\n" + super().__str__()


class OrOperation(Operation):
    def __init__(self, operands, **kwargs):
        super().__init__(operands, **kwargs)

    # def __str__(self):
    #     return "or [\n" + super().__str__()


class AssignmentOperation(Operation):
    def __init__(self, variable: str, predicate: Dict[str, Any], value: Any):
        super().__init__()
        self.variable = variable
        self.predicate = Operation.from_dict(predicate)
        self.value = value

    # def __str__(self):
    #     return f"({str(self.predicate)}) => {self.variable} = {self.value}"

class IfOperation(Operation):
    def __init__(self, operands: List[Dict[str, Any]], variable: str, value: Any):
        print(operands)
        super().__init__(operands)


class IfElseOperation(Operation):
    def __init__(self, operands: List[Dict[str, Any]]):
        super().__init__(operands)
    
class BaseTransformer(ABC):
    def __init__(self):
        super().__init__()
        self.indent = 0

    @property
    def s(self) -> str:
        return " " * self.indent

class StringTransformer(BaseTransformer):
    
    def EnterEqualOperation(self, other: EqualOperation):
        print(f"{other.target} == {other.value}", end='')
    
    def EnterInOperation(self, other: InOperation):
        print(f"{other.target} in ({', '.join([str(x) for x in other.value])})", end="")
    
    def WhileIfElseOperation(self, other: IfElseOperation):
        print(f"\nelse ", end='')

    def EnterIfOperation(self, other: IfOperation):
        print(f"if (", end='')

    def ExitIfOperation(self, other: IfOperation):
        print(f"):", end='')

    



class PandasTransformer(BaseTransformer):
    def __init__(self, df: str, variable: str):
        super().__init__()
        self.variable = variable
        self.df = df

    def EnterInOperation(self, other: InOperation):
        res = f'{self.s}({self.df}["{other.target}"].isin({str(other.value)}))'
        print(res, end="")

    def EnterAndOperation(self, other: AndOperation):
        print(self.s + "(", end="")
        self.indent += 2

    def WhileAndOperation(self, other: AndOperation):
        print(" &")

    def ExitAndOperation(self, other: AndOperation):
        self.indent -= 2
        print(")", end="")

    def EnterEqualOperation(self, other: EqualOperation):
        print(f'({self.df}["{other.target}"] == {other.value})', end="")

    def EnterNotOperation(self, other: NotOperation):
        print(f"{self.s}~", end="")

    def EnterOrOperation(self, other: OrOperation):
        print("(", end="")
        self.indent += 2

    def WhileOrOperation(self, other: OrOperation):
        print(" |")

    def ExitOrOperation(self, other: OrOperation):
        print(")")
        self.indent -= 2


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
    v = PandasTransformer(df="df", variable="var1")
    #res1.walk(v)

    v2 = StringTransformer()
    #res1.walk(v2)


    # reading from json file
    import json

    with open("specs/example02.json", "r") as fin:
        j = json.load(fin)

    res2 = Operation.from_dict(j)
    res2.walk(v2)
    # print(res2)
