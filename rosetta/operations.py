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


# register operations with factory
Operation.register_operation("and", AndOperation)
Operation.register_operation("eq", EqualOperation)
Operation.register_operation("not", NotOperation)
Operation.register_operation("or", OrOperation)
Operation.register_operation("in", InOperation)
Operation.register_operation("assign", AssignmentOperation)
Operation.register_operation("ifelse", IfElseOperation)
Operation.register_operation("if", IfOperation)
