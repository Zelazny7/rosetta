import ast
from typing import List, Optional, Union
from io import TextIOWrapper


class PandasVisitor(ast.NodeVisitor):
    def __init__(self, data_frame_id: str = "df"):
        super().__init__()
        self.indent: int = 0
        self.result: List[str] = []
        self.if_counter: int = 0
        self.if_assign_name: Optional[str] = None
        self.data_frame_id = data_frame_id

    def parse(self, file: Union[str, TextIOWrapper]):
        if isinstance(file, str):
            with open(file, "r") as fin:
                tree = ast.parse(fin.read())
        elif isinstance(file, TextIOWrapper):
            tree = ast.parse(file.read())
        else:
            tree = file

        self.visit(tree)
        return ''.join(self.result)

    def visit_USub(self, node):
        self.result += ["-"]

    def visit_Gt(self, node):
        self.result += [" > "]

    def visit_BoolOp(self, node):
        op = " & " if isinstance(node, ast.And) else " | "
        self.result += ["("]
        super().visit(node.values[0])
        self.result += [") ", op, " ("]
        super().visit(node.values[1])
        self.result += [")"]

    def visit_Eq(self, node):
        self.result += [" == "]

    def visit_Compare(self, node: ast.Compare):
        if isinstance(node.ops[0], ast.In):
            super().visit(node.left)
            self.result += [".isin("]
            super().visit(node.comparators[0])
            self.result += [")"]
        elif isinstance(node.ops[0], ast.NotIn):
            self.result += ["~"]
            super().visit(node.left)
            self.result += [".isin("]
            super().visit(node.comparators[0])
            self.result += [")"]
        else:
            super().generic_visit(node)

    def visit_Attribute(self, node):
        key = node.value.id + node.attr
        if key.lower() == "npnan":
            self.result.append("np.nan")

    def visit_Call(self, node):
        func = node.func.id
        if func == "min":
            self.result += ["np.minimum("]
        elif func == "max":
            self.result += ["np.maximum("]
        elif func == "floor":
            self.result += ["np.floor("]
        else:
            raise ValueError(f"Function, {func}, not supported. Line: {node.lineno}")

        self.visit(node.args[0])
        self.result += [", "]
        self.visit(node.args[1])
        self.result += [")"]

    def visit_If(self, node):
        if self.if_counter == 0:
            self.if_assign_name = node.body[0].targets[0].id
            self.result.append(f'{self.data_frame_id}["{self.if_assign_name}"] = ')
        else:
            self.result.append(", ")

        self.result.append(f"np.where(\n  ")

        self.if_counter += 1
        self.generic_visit(node)

        self.result.append(")")
        if self.if_assign_name is None:
            # add blank line between if blocks
            self.result.append("\n\n")

        self.if_counter -= 1
        self.if_assign_name = None

    def visit_Assign(self, node):
        if self.if_counter > 0:
            self.result.append(", ")
        super().generic_visit(node)

    def visit_Name(self, node):
        if node.id != self.if_assign_name:
            self.result += [f'{self.data_frame_id}["{node.id}"]']
        super().generic_visit(node)
    
    def visit_Store(self, node):
        if self.if_assign_name is None:
            self.result.append(" = ")

    def visit_Constant(self, node):
        if self.if_counter > 0:
            if isinstance(node.value, str):
                self.result += [f'"{node.value}"']
            else:
                self.result += [str(node.value)]

        super().generic_visit(node)

    def visit_List(self, node):
        self.result += ["["]
        for i, el in enumerate(node.elts):
            super().visit(el)
            if i < len(node.elts) - 1:
                self.result += [", "]

        self.result += ["]"]
