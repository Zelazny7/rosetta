from rosetta.visitors import PandasVisitor
import black, ast, tempfile
import seaborn as sns

## parse a file
if __name__ == "__main__":
    import numpy as np

    df = sns.load_dataset('iris')

    pandas_visitor = PandasVisitor()

    # result = pandas_visitor.parse("specs/example03.py")

    # print(black.format_str(result, mode=black.FileMode()))

    result = pandas_visitor.parse("specs/example03.py")
    f = compile(ast.parse(result), filename='tmp.txt', mode="exec")


    exec(f)

    print(df.head())

    # ast.
