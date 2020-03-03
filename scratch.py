from rosetta import Operation, PandasVisitor


if __name__ == "__main__":
    d = {
        "op": "and",
        "operands": [
            {"op": "eq", "target": "mpg", "value": 25},
            {
                "op": "not",
                "operands": [
                    {
                        "op": "or",
                        "operands": [
                            {"op": "eq", "target": "disp", "value": 10},
                            {"op": "in", "target": "cyl", "value": [2, 4, 6, 8]},
                        ],
                    }
                ],
            },
        ],
    }

    # create compound operation from dictionary
    res1 = Operation.from_dict(d)

    # demonstrate variable walking
    v = PandasVisitor(df="df", variable="var1")
    v.visit(res1)
    # res1.walk(v)

    # v2 = StringTransformer()
    # res1.walk(v2)

    # reading from json file
    # import json

    # with open("specs\\example02.json", "r") as fin:
    #     j = json.load(fin)

    # res2 = Operation.from_dict(j)
    # res2.walk(v2)
    # print(res2)
