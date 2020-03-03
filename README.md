# rosetta

Specify variables in json, output them to your language.

## Example

This is a simple json object representing  variable operations. This is not a complete 
example. A user can implement the BaseTransformer class that visits every operation
and executes code before, while, and after each nested operation.

In this manner, variable logic can be specified in a language agnostic way and output to 
any other language that has a concrete BaseTransformer.

```json
json = {
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
                            "value": [
                                2,
                                4,
                                6,
                                8
                            ]
                        },
                    ],
                }
            ],
        },
    ],
}
```

I have created a very simple PandasTransformer that has methods that trigger when various
operations are visited:

```python
from rosetta import Operation, PandasTransformer

res = Operation.from_dict(json)
tf = PandasTransformer(df="df", variable="new_variable")
tf.walk(res)
```

Ouputs the following code:

```python
((df["mpg"] == 25) &
  ~((df["disp"] == 10) |
    (df["cyl"].isin([2, 4, 6, 8])))
```

