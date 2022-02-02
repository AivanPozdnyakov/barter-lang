from lark import Lark, Tree, Token
from llvm.brand_compiler import finalize_llvm
from llvm_backend import parse_function


def transform(tree):
    if type(tree.data) == Token:
        tree.data = tree.data.value
    for i, child in enumerate(tree.children):
        if type(child) == Token:
            tree.children[i] = child.value
        if type(child) == Tree:
            transform(child)
            children = child.children
            if child.data in ("params", "dec_params"):
                tree.children[i] = (child.data, children)
                continue
            if len(children) == 1:
                children = child.children[0]
            tree.children[i] = (child.data, children) if len(children) else child.data
            # else:

# "../res/examples/fib.barter"
def build_ast_from_file(filename: str):
    with open("../res/bl_lexer_rules.txt", "r") as f:
        parser = Lark(f.read(), parser='lalr')
    with open(filename, "r") as f:
        ast = parser.parse(f.read())
    transform(ast)
    ast = ast.children
    return ast

    # for f in ast:
    #     tag, data = f
    #     if tag == "function":
    #         parse_function(data)
    #     else:
    #         assert 0, f"Unhandled tag {tag}"
    # print(generate_llvm(ctx))
