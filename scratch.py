from rosetta.visitors import PandasVisitor
import black, ast

## parse a file
if __name__ == "__main__":
    
    pandas_visitor = PandasVisitor()

    result = pandas_visitor.parse('specs/example03.py')
    
    print(black.format_str(result, mode=black.FileMode()))
