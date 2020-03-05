import ast
from collections import defaultdict

def unroll_if(node, res=None):
    print("entering")
    if res is None:
        res = []
    
    for child in ast.iter_child_nodes(node):
        res.append(child)
        # if isinstance(child, ast.If):
        #     res.append(", np.where(")
        #     unroll_if(child.test, res)
        #     unroll_if(child.body[0], res)
        #     res.append(")")
        # elif isinstance(child, ast.Compare):
        #     res.append(child.comparators[0])
        #     unroll_if(child.comparators[0], res)
        # elif isinstance(child, ast.Assign):
        #     unroll_if(child.value, res)
            # self.visit(child.value)
    return res


class Visitor(ast.NodeVisitor):
    def __init__(self):
        super().__init__()
        self.if_counter = 0
        self.if_assign_name = None

    def visit_If(self, node):
        if self.if_counter == 0:
            self.if_assign_name = node.body[0].targets[0].id
            print(f"{self.if_assign_name} = ", end="")
        else:
            print(", ", end="")
        
        print("np.where(", end="")
        self.if_counter += 1
        self.generic_visit(node)
        print(")", end="")
        self.if_counter -= 1
        self.if_assign_name = None
    
    def visit_Assign(self, node):
        if self.if_counter > 0:
            print(", ", end="")
        super().generic_visit(node)
    
    def visit(self, node):
        super().visit(node)

    def visit_Eq(self, node):
        print(" == ", end="")
        super().generic_visit(node)
    
    def visit_Compare(self, node: ast.Compare):
        super().generic_visit(node)

    def visit_Name(self, node):
        if node.id != self.if_assign_name:
            print(f"{node.id}", end="")
        super().generic_visit(node)
    
    def visit_Expr(self, node):
        super().generic_visit(node)
    
    def visit_Constant(self, node):
        if self.if_counter > 0:
            print(f"{node.value}", end="")
            #print(f"{node.id}", end="")
        super().generic_visit(node)
    
    def visit_USub(self, node):
        print("-", end="")
    
    def visit_BoolOp(self, node):
        if isinstance(node, ast.And):
            op = "and"
        else:
            op = "or"
        
        print("(", end="")
        super().visit(node.values[0])
        print(")", end="")
        print(f" {op} ", end="")
        print("(", end="")
        super().visit(node.values[1])
        print(")", end="")
        
    def visit_Gt(self, node):
        print(" > ", end="")
        super().generic_visit(node)

## parse a file
if __name__ == "__main__":

    v = Visitor()

    with open('specs/example03.py') as fin:
        tree = ast.parse(fin.read())
        
        res = v.visit(tree)
        # print(res)


def compile_func(func):
    def magic(func)

