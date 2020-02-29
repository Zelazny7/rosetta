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
            res = klass(**x)
            operands = x.get("operands", None)
            
            if operands is not None:
                res = cast(MultiPredicate, res)
                res.operands = [cast(Predicate, Operation.from_dict(d)) for d in operands]

            return res

    def __init__(self, **kwargs):
        super().__init__()
    
    @property
    def indent(self):
        return Operation._indent
    
    @indent.setter
    def indent(self, value):
        Operation._indent = value
    
class Predicate(Operation, ABC):
    pass


class SinglePredicate(Predicate, ABC):
    """SinglePredicate only performs one operation"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class EqualPredicate(Predicate):
    def __init__(self, target: str, value: Any):
        super().__init__()
        self.target = target
        self.value = value
    
    def __str__(self) -> str:
        return f"{self.target} == {self.value}"

class InPredicate(Predicate):
    def __init__(self, target: str, values: List[Any]):
        super().__init__()
        self.target = target
        self.values = values
    
    def __str__(self) -> str:
        return f"{self.target} in ({', '.join([str(x) for x in self.values])})"


class MultiPredicate(Predicate, ABC):
    """MultiPredicates combine collections of SinglePredicates"""
    def __init__(self, operands: List[Predicate], **kwargs):
        super().__init__(**kwargs)
        self._operands = operands

    @property
    def operands(self) -> List[Predicate]:
        return self._operands
    
    @operands.setter
    def operands(self, value):
        self._operands = value
    
    def __str__(self):
        self.indent += 2
        res =  f'\n'.join([(' ' * self.indent) + str(x) for x in self.operands])
        self.indent -= 2
        return res + '\n' + ' ' * self.indent + ']'

class AndPredicate(MultiPredicate):
    def __init__(self, operands, **kwargs):
        super().__init__(operands, **kwargs)
    
    def __str__(self):
        return "and [\n" + super().__str__()


class NotPredicate(MultiPredicate):
    def __init__(self, operands, **kwargs):
        super().__init__(operands, **kwargs)
    
    def __str__(self):
        return "not [\n" +  super().__str__()

class OrPredicate(MultiPredicate):
    def __init__(self, operands, **kwargs):
        super().__init__(operands, **kwargs)
    
    def __str__(self):
        return  "or [\n" +  super().__str__()


if __name__ == "__main__":
    d = {
        "op": "and",
        "operands": [
            {
                "op": "eq",
                "target": "mpg",
                "value": 25
            },
            {
                "op": "not",
                "operands": [
                    {
                        "op": "or",
                        "operands": [
                            {
                                "op": "eq",
                                "target": "disp",
                                "value": 10
                            },
                            {
                                "op": "in",
                                "target": "cyl",
                                "values": [2,4,6,8]
                            }
                        ]
                    }

                ]
            }
        ]
        }
    
    Operation.register_operation("and", AndPredicate)
    Operation.register_operation("eq", EqualPredicate)
    Operation.register_operation("not", NotPredicate)
    Operation.register_operation("or", OrPredicate)
    Operation.register_operation("in", InPredicate)

    res1 = Operation.from_dict(d)
    print(res1)

    import json
    with open('specs/example01.json', 'r') as fin:
        j = json.load(fin)
    
    res2 = Operation.from_dict(j)
    print(res2)
    
