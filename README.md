# rosetta

Specify variable transformations in python, output them to your language.

## Example

Below is some python code that describes variable transformations on a single input
record. The input record is implicit just like it is for a SAS dataset. Using the python `ast` module, `rosetta` can transform the row-by-row transformation logic into
vectorized logic designed for `pandas` and `numpy`.

```python
if sepal_length > 6 or sepal_width > 5:
    new_var = "flower1"
elif species in ['setosa','virginica']:
    new_var = 'ends in A'
elif petal_length > petal_width:
    new_var = petal_width
else:
    new_var = np.nan
```

I have created a very simple PandasTransformer that has methods that trigger when various
operations are visited:

```python
from rosetta.visitors import PandasVisitor
import black, ast

pandas_visitor = PandasVisitor()
result = pandas_visitor.parse("specs/example03.py")
print(black.format_str(result, mode=black.FileMode()))
```

Ouputs the following code which is formatted by `black`:

```python
df["new_var"] = np.where(
    (df["sepal_length"] > 6) | (df["sepal_width"] > 5),
    "flower1",
    np.where(
        df["species"].isin(["setosa", "virginica"]),
        "ends in A",
        np.where(df["petal_length"] > df["petal_width"], df["petal_width"], np.nan),
    ),
)
```

## Running the code

Once translated the code can be compiled and executed. If python can find the items referenced in the code, they will be executed. In this case, we need to have a 
DataFrame named `df` and the numpy module imported as `np`:

```python
import seaborn as sns
import numpy as np

df = sns.load_dataset('iris')
pandas_visitor = PandasVisitor()
result = pandas_visitor.parse("specs/example03.py")

f = compile(ast.parse(result), filename='tmp.txt', mode="exec")
exec(f)

> print(df.head())

   sepal_length  sepal_width  petal_length  petal_width species    new_var
0           5.1          3.5           1.4          0.2  setosa  ends in A
1           4.9          3.0           1.4          0.2  setosa  ends in A
2           4.7          3.2           1.3          0.2  setosa  ends in A
3           4.6          3.1           1.5          0.2  setosa  ends in A
4           5.0          3.6           1.4          0.2  setosa  ends in A
```

