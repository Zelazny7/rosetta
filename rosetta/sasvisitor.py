import ast
from typing import List, Optional, Union
from io import TextIOWrapper


class SASVisitor(ast.NodeVisitor):
    def __init__(self):
        super().__init__()
        self.indent: int = 0
        self.result: List[str] = []
        self.if_counter = 0
        self.entered = False
        self.last_else = False

    def parse(self, code: str):
        tree = ast.parse(code)
        self.visit(tree)
        return ''.join(self.result)

    def visit_USub(self, node):
        self.result += ["-"]

    def visit_Gt(self, node):
        self.result += [" > "]

    def visit_BoolOp(self, node):
        op = " and " if isinstance(node, ast.And) else " or "
        self.result += ["("]
        super().visit(node.values[0])
        self.result += [") ", op, " ("]
        super().visit(node.values[1])
        self.result += [")"]

    def visit_Eq(self, node):
        self.result += [" = "]

    def visit_Compare(self, node: ast.Compare):
        self.result.append("(")
        if isinstance(node.ops[0], ast.In):
            super().visit(node.left)
            self.result += [" in "]
            super().visit(node.comparators[0])
        elif isinstance(node.ops[0], ast.NotIn):
            super().visit(node.left)
            self.result += ["not in"]
            super().visit(node.comparators[0])
        else:
            super().generic_visit(node)
        self.result.append(")")

    def visit_Call(self, node):
        func = node.func.id
        if func == "min":
            self.result += ["min("]
        elif func == "max":
            self.result += ["max("]
        elif func == "floor":
            self.result += ["floor("]
        else:
            raise ValueError(f"Function, {func}, not supported. Line: {node.lineno}")

        self.visit(node.args[0])
        self.result += [", "]
        self.visit(node.args[1])
        self.result += [")"]

    def visit_If(self, node):

        # special condtion for last chunk
        if isinstance(node.orelse[0], ast.Assign):
            # self.result.append("\nelse if ")
            super().visit(node.test)
            self.result.append("\n    then ")
            super().visit(node.body[0])
            self.result.append("\nelse ")
            super().visit(node.orelse[0])
            self.result.append("\n\n")
        else:
            if self.entered is False:
                self.entered = True
                self.result.append("\nif ")
            super().visit(node.test)
            self.result.append("\n    then ")
            super().visit(node.body[0])
            self.result.append("\nelse if ")
            super().visit(node.orelse[0])
        
        self.entered = False

    def visit_Assign(self, node):
        super().generic_visit(node)
        self.result.append(";")
        
    def visit_Name(self, node):
        self.result += node.id
        super().generic_visit(node)
    
    def visit_Store(self, node):
        self.result.append(" = ")
        super().generic_visit(node)

    def visit_Constant(self, node):
        if isinstance(node.value, str):
            self.result += [f'"{node.value}"']
        else:
            self.result += [str(node.value)]

        super().generic_visit(node)

    def visit_List(self, node):
        self.result += ["("]
        for i, el in enumerate(node.elts):
            super().visit(el)
            if i < len(node.elts) - 1:
                self.result += [", "]

        self.result += [")"]
