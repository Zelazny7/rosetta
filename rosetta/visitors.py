import ast
from typing import List, Optional, Union, Dict
from io import TextIOWrapper

function_map: Dict[str, Dict[str, str]] = {
    "PandasVisitor": {"min": "np.minimum", "max": "np.maximum", "floor": "np.floor"},
    "SASVisitor": {"min": "min", "max": "max", "floor": "floor"},
}


class BaseVisitor(ast.NodeVisitor):
    def __init__(self):
        super().__init__()
        self.result: List[str] = []
        self.meta: bool = False

        self.binop = {ast.Div: " / ", ast.Mult: " * ", ast.Add: " + ", ast.Sub: " - "}

    def parse(self, code: str):
        tree = ast.parse(code)
        self.visit(tree)
        return "".join(self.result)

    def get_function(self, node: ast.Call) -> str:
        klass = self.__class__.__name__
        _map = function_map.get(klass, None)
        if _map is None:
            raise ValueError(f"Class, {klass}, not found in function_map")
        res = _map.get(node.func.id, None)
        if res is None:
            raise ValueError(
                f"Function, {node.func.id}, not supported. Line: {node.lineno}"
            )
        return res

    def get_binop(self, node: ast.BinOp) -> str:
        res = self.binop.get(type(node.op))
        if res is None:
            raise ValueError(f"Operator, {type(node.op)}, not found.")
        return res


# function map


class PandasVisitor(BaseVisitor):
    def __init__(self, data_frame_id: str = "df"):
        super().__init__()
        self.indent: int = 0
        self.if_counter: int = 0
        self.if_assign_name: Optional[str] = None
        self.data_frame_id = data_frame_id

    def visit_Dict(self, node):
        pass

    def visit_USub(self, node):
        self.result += ["-"]

    def visit_Gt(self, node):
        self.result += [" > "]

    def visit_BinOp(self, node):
        self.result.append("(")
        super().visit(node.left)
        self.result.append(f" {self.get_binop(node)} ")
        super().visit(node.right)
        self.result.append(")")

    def visit_BoolOp(self, node):
        op = "and" if isinstance(node, ast.And) else "or"
        self.result.append("(")
        super().visit(node.values[0])
        self.result.append(f") {op} (")
        super().visit(node.values[1])
        self.result.append(")")

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
        fun = self.get_function(node)
        if fun is None:
            raise ValueError(
                f"Function, {node.func.id}, not supported. Line: {node.lineno}"
            )

        self.result.append("(")
        for i, arg in enumerate(node.args):
            super().visit(arg)
            if i < len(node.args) - 1:
                self.result.append(", ")

        self.result.append(")")

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


## SAS Visitor ##


class SASVisitor(BaseVisitor):
    def __init__(self):
        super().__init__()
        # self.indent: int = 0
        self.entered = False
        self.meta = False

    def visit_Dict(self, node):
        self.meta = True
        for i, (key, val) in enumerate(zip(node.keys, node.values)):
            self.result.append("*@")
            super().visit(key)
            self.result.append(": ")
            super().visit(val)
            self.result.append(";")
            if i < len(node.keys) - 1:
                self.result.append("\n")
        self.meta = False

    def parse(self, code: str):
        tree = ast.parse(code)
        self.visit(tree)
        return "".join(self.result)

    def visit_USub(self, node):
        self.result.append("-")

    def visit_Gt(self, node):
        self.result.append(" > ")

    def visit_BinOp(self, node):
        self.result.append("(")
        super().visit(node.left)
        self.result.append(f"{self.get_binop(node)}")
        super().visit(node.right)
        self.result.append(")")

    def visit_BoolOp(self, node):
        op = " and " if isinstance(node, ast.And) else " or "
        super().visit(node.values[0])
        self.result.append(f"{op}")
        super().visit(node.values[1])

    def visit_Eq(self, node):
        self.result.append(" = ")

    def visit_Compare(self, node: ast.Compare):
        self.result.append("(")
        if isinstance(node.ops[0], ast.In):
            super().visit(node.left)
            self.result.append(" in ")
            super().visit(node.comparators[0])
        elif isinstance(node.ops[0], ast.NotIn):
            super().visit(node.left)
            self.result.append("not in")
            super().visit(node.comparators[0])
        else:
            super().generic_visit(node)
        self.result.append(")")

    def visit_Call(self, node):
        fun = self.get_function(node.func.id)

        self.result.append("(")
        for i, arg in enumerate(node.args):
            super().visit(arg)
            if i < len(node.args) - 1:
                self.result.append(", ")

        self.result.append(")")

    def visit_If(self, node):

        # special condtion for last chunk
        if isinstance(node.orelse[0], ast.Assign):
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
        self.result.append(node.id)
        super().generic_visit(node)

    def visit_Store(self, node):
        self.result.append(" = ")
        super().generic_visit(node)

    def visit_Constant(self, node):
        if self.meta:
            self.result.append(str(node.value))
        elif isinstance(node.value, str):
            self.result.append(f'"{node.value}"')
        else:
            self.result.append(str(node.value))

        super().generic_visit(node)

    def visit_List(self, node):
        self.result += ["("]
        for i, el in enumerate(node.elts):
            super().visit(el)
            if i < len(node.elts) - 1:
                self.result.append(", ")
        self.result.append(")")
