from rosetta.visitors import PandasVisitor
import black, ast
import inspect
import textwrap
# import seaborn as sns
import ast



## try to implement a context manager

def datastep(func, df="df"):
    v = PandasVisitor()

    s = inspect.getsource(func).split('\n')
    s = '\n'.join(s[2:]) # remove decorator and signature

    # dedent before parsing
    v.parse(ast.parse(textwrap.dedent(s)))
    
    # join and format
    body = black.format_str(''.join(v.result), mode=black.FileMode())

    # compile
    f = compile(body, mode="exec", filename="tmp.txt")
    def magic():
        exec(f)
    
    return magic

@datastep
def hello():
    if sepal_length > 6 or sepal_width > 5:
        new_var = "flower1"
    elif species in ['setosa','virginica']:
        new_var = 'ends in A'
    elif petal_length > petal_width:
        new_var = petal_width
    else:
        new_var = np.nan
    
    if sepal_length > 6 or sepal_width > 5:
        new_var2 = "flower1"
    elif species in ['setosa','virginica']:
        new_var2 = 'ends in A'
    elif petal_length > petal_width:
        new_var2 = petal_width
    else:
        new_var2 = np.nan
    
    new_var3 = new_var2


if __name__ == "__main__":
    import ast

    import numpy as np
    import seaborn as sns
    df = sns.load_dataset('iris')
    
    hello()

    print(df.tail())
    

    


# print(inspect.getsource(hello)[1:])
