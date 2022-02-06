from lark import Lark, Tree, Token


def transform(tree):
    if type(tree.data) == Token:
        tree.data = tree.data.value
    for i, child in enumerate(tree.children):
        if type(child) == Token:
            tree.children[i] = child.value
        if type(child) == Tree:
            transform(child)
            children = child.children
            if child.data in ("params", "dec_params", "macro_params", "importc_params", "system_call_params", "struct_params"):
                tree.children[i] = (child.data, children)
                continue
            if len(children) == 1:
                children = child.children[0]
            tree.children[i] = (child.data, children) if len(children) else child.data
            if type(tree.children[i]) == str and tree.children[i].startswith("ptr_"):
                tree.children[i] = tree.children[i].replace("ptr_", "") + "*"
            # else:

# "../res/examples/fib.barter"
def build_ast_from_file(filename: str):
    with open("bl_lexer_rules.txt", "r") as f:
        parser = Lark(f.read(), parser='lalr')
    with open(filename, "r") as f:
        ast = parser.parse(f.read())
    transform(ast)
    ast = ast.children
    return ast

def build_ast(rules: str, listing: str):
    parser = Lark(rules, parser='lalr')
    ast = parser.parse(listing)
    transform(ast)
    ast = ast.children
    return ast
