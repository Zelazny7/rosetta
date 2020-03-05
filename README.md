# rosetta

Specify variable transformations in python, output them to your language.

## Example

Below is some python code that describes variable transformations on a single input
record. The input record is implicit just like it is for a SAS dataset. Using the python `ast` module, `rosetta` can transform the row-by-row transformation logic into
vectorized logic designed for `pandas` and `numpy`.

```python
if add1naprop == 1 or avmvalue > 200000:
    iv_add1naprop = -1
elif add1naprop == 2:
    iv_add1naprop = 0
elif ((add1naprop == 4) and (avmvalue not in [-1, 25])) or (add1naprop > 4):
    iv_add1naprop = min(300_000, avmvalue)
else:
    iv_add1naprop = np.nan
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
df["iv_add1naprop"] = np.where(
    (df["add1naprop"] == 1) or (df["avmvalue"] > 200000),
    -1,
    np.where(
        df["add1naprop"] == 2,
        0,
        np.where(
            ((df["add1naprop"] == 4) or (~df["avmvalue"].isin([-1, 25])))
            or (df["add1naprop"] > 4),
            np.minimum(300000, df["avmvalue"]),
            np.nan,
        ),
    ),
)
```

