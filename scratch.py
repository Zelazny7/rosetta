from rosetta.visitors import PandasVisitor
from rosetta.sasvisitor import SASVisitor
import black, ast, tempfile
# import seaborn as sns

## parse a file
if __name__ == "__main__":
    # import numpy as np

    # df = sns.load_dataset('iris')

    sas_visitor = SASVisitor()

    pandas_visitor = PandasVisitor()

    # result = pandas_visitor.parse("specs/example03.py")

    

    with open("specs/example03.py", "r") as fin:
        code = fin.read()

    result1 = pandas_visitor.parse("specs/example03.py")
    result2 = sas_visitor.parse(code)
    
    print(black.format_str(result1, mode=black.FileMode()))
    
    print(result2)
    #f = compile(ast.parse(result), filename='tmp.txt', mode="exec")


    #exec(f)

    #print(df.head())

    # ast.
