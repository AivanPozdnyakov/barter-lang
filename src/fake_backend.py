from collections import defaultdict
from typing import Literal

from rich import inspect

typeof = Literal["int"]

result = []


def as_dict(iterable) -> dict:
    result_dict = defaultdict(list)
    for it in iterable:
        key, value = it
        result_dict[key].append(value)
    for key, value in result_dict.items():
        if len(value) == 1:
            result_dict[key] = value[0]
    return dict(result_dict)


def parse_function(data):
    # f = as_dict(data)
    function_name, params, return_type = data[:3]  # f["function_name"], f["dec_params"], f["return_type"], f["body"]
    function_body = data[3:]
    s = f"fake-function `{function_name}` ({params}) -> {return_type}"
    result.append(s)
    print(function_body)
    parse_block(function_body)


def parse_block(body):
    for statement in body:
        parse_statement(statement)


def parse_if(data):
    expr, block = data[0], data[1:]
    parse_expr(expr)
    result.append("if last is true")
    parse_block(block)
    result.append("endif")


def parse_return(data):
    parse_expr(data)
    result.append("fake return")
    pass


def parse_while(data):
    expr, block = data[0], data[1:]
    parse_expr(expr)
    result.append("while last is true")
    parse_block(block)
    result.append("endwhile")


def parse_expr(data):
    tag, data = data
    if tag == "number":
        result.append(f"push {data}")
    elif tag == "var":
        result.append(f"load {data}")
    elif tag in ("sub", "add", "mul", "div", "lt"):
        parse_expr(data[0])
        parse_expr(data[1])
        result.append(f"apply binary {tag}")
    elif tag == "function_call":
        function_name, params = data
        _, params_data = params
        for param in params_data:
            parse_expr(param)
        result.append(f"apply function {function_name}")
    else:
        assert 0, f"unknown tag {tag}"


def parse_declare_variable(data):
    typeof, name, expr = data
    parse_expr(expr)
    result.append(f"declare variable {(typeof, name)} pop)")


def parse_assign_variable(data):
    name, expr = data
    parse_expr(expr)
    result.append(f"assign variable {name} pop)")


def parse_statement(statement):
    # if statement == "end":
    #     return
    tag, data = statement
    if tag == "if":
        return parse_if(data)
    elif tag == "return":
        return parse_return(data)
    elif tag == "expression":
        return parse_expr(data)
    elif tag == "while":
        return parse_while(data)
    elif tag == "declare_variable":
        return parse_declare_variable(data)
    elif tag == "assigment":
        return parse_assign_variable(data)
    assert 0, f"Unhandled tag {tag}"


def fake_assigment(variable_name: str, expr) -> str:
    return f"fake-assigment: {variable_name} = {expr}"


def fake_expression(t):
    print(t, inspect(t))
