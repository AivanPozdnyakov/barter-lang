from typing import Literal

from llvm.basic_instructions import *  # push_number
from llvm.control_flow_instructions import *
from llvm.struct import FunctionSignature

typeof = Literal["int"]

result = []
putchar_signature = FunctionSignature(1)
signatures = {"putchar": putchar_signature}
ctx = Context(signatures=signatures)


def parse_function(data):
    function_name, params, return_type = data[:3]
    if len(params):
        params = [tuple(param[1]) for param in params[1]]
    else:
        params = []
    function_body = data[3:]
    function(ctx, function_name, params, return_type)
    parse_block(function_body)
    end_function(ctx)


def parse_block(body):
    for statement in body:
        parse_statement(statement)


def parse_if(data):
    expr, block = data[0], data[1:]
    parse_expr(expr)
    branch(ctx)
    parse_block(block)
    end_branch(ctx)


def parse_return(data):
    parse_expr(data)
    ret(ctx)
    pass


def parse_while(data):
    expr, block = data[0], data[1:]
    loop_header(ctx)
    parse_expr(expr)
    loop(ctx)
    parse_block(block)
    end_loop(ctx)


def parse_expr(data):
    tag, data = data
    if tag == "number":
        push_number(ctx, data)
    elif tag == "var":
        push_variable(ctx, data)
    elif tag in ("sub", "add", "mul", "div", "lt", "be"):
        parse_expr(data[0])
        parse_expr(data[1])
        apply_binary_operation(ctx, tag)
    elif tag == "function_call":
        function_name, params = data
        _, params_data = params
        for param in params_data:
            parse_expr(param)
        call_function(ctx, function_name)
    else:
        assert 0, f"unknown tag {tag}"


def parse_declare_variable(data):
    typeof, name, expr = data
    declare(ctx, name)
    parse_expr(expr)
    assign(ctx, name)
    # typeof use


def parse_assign_variable(data):
    name, expr = data
    parse_expr(expr)
    assign(ctx, name)


def parse_statement(statement):
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
