from collections import defaultdict

from lark import Lark, Tree, Token

from fake_backend import parse_function, result


# class MyTransformer(Transformer):
#     def function(self, items):
#         function_name, params, return_type, body = items
#         return {"function_name": function_name, "params": params,
#                 "return_type": return_type}
#
#     def function_name(self, items: list[Token]) -> str:
#         return items[0].value
#
#     def return_type(self, items):
#         return items[0].data

def transform(tree):
    if type(tree.data) == Token:
        tree.data = tree.data.value
    for i, child in enumerate(tree.children):
        if type(child) == Token:
            tree.children[i] = child.value
        if type(child) == Tree:
            # if len(child.children):
            transform(child)
            children = child.children
            # if tree.data == "body":
            #     print("hey", tree.children)
            if child.data == "params":
                tree.children[i] = (child.data, children)
                continue
            if len(children) == 1:
                children = child.children[0]
            tree.children[i] = (child.data, children) if len(children) else child.data
            # else:

def main() -> None:
    with open("../res/bl_lexer_rules.txt", "r") as f:
        parser = Lark(f.read(), parser='lalr')
    with open("../res/examples/fib.barter", "r") as f:
        r = parser.parse(f.read())
    # r = MyTransformer().transform(r)
    transform(r)
    r = r.children
    # print(r.pretty())
    for f in r:
        tag, data = f
        if tag == "function":
            parse_function(data)
        else:
            assert 0, f"Unhandled tag {tag}"
    print("\n".join(result))
        # print(as_dict(function))


if __name__ == '__main__':
    main()
