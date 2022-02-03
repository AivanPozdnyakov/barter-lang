from llvm.basic_instructions import *  # push_number
from llvm.control_flow_instructions import *
from llvm.struct import LLVM, FunctionSignature, VAR, GENERIC_TYPE, NUMBER
from src.llvm.ptr_instructions import deref_ptr_and_push, shift, assign_ptr, create_array_and_push


def parse_importc(ctx: Context, data) -> None:
    name, params, return_type = data
    ctx.signatures[name] = FunctionSignature(params[1], return_type)
    params = ",".join(params[1])
    ctx.listing.append(f"declare {return_type} @{name}({params})")


def parse_ast(ctx: Context, ast) -> None:
    for f in ast:
        tag, data = f
        if tag == "function":
            parse_function(ctx, data)
        elif tag == "importc":
            parse_importc(ctx, data)
        else:
            assert 0, f"Unhandled tag {tag}"


def transform_params(params) -> list[tuple[LLVM.type, str]]:
    if len(params):
        params = [tuple(param[1]) for param in params[1]]
    else:
        params = []
    return [(typeof, name) for typeof, name in params]


def parse_function_header(ctx: Context, function_name: str, params, return_type: LLVM.type):
    params = transform_params(params)
    params_types = [typeof for typeof, _ in params]
    ctx.signatures[function_name] = FunctionSignature(params_types, return_type)
    params_as_str = ",".join([str(param_type) for param_type in params_types])
    ctx.listing.append(f"define {return_type} @{function_name}({params_as_str}){{")
    assert len(set([name for _, name in params])) == len(params)
    for i, param in enumerate(params):
        typeof, name = param
        llvm_declare(ctx, name, typeof)
        ctx.variables[name] = typeof
        ctx.parameters.append(f"%{i}")
        llvm_assign(ctx, name, typeof)
    add_register(ctx, len(params))


def parse_function(ctx: Context, data):
    function_name, params, return_type = data[:3]
    function_body = data[3:]
    parse_function_header(ctx, function_name, params, return_type)
    ctx.current_return_type = return_type
    if return_type != "void":
        llvm_declare(ctx, "return", return_type)
    parse_block(ctx, function_body)
    llvm_end_function(ctx)


def parse_block(ctx: Context, body):
    for statement in body:
        parse_statement(ctx, statement)


def parse_if(ctx: Context, data):
    expr, block = data[0], data[1:]
    expr_type = parse_expr(ctx, expr)
    assert expr_type == LLVM.bool, expr_type
    llvm_branch(ctx)
    parse_block(ctx, block)
    llvm_branch_end(ctx)


def parse_while(ctx: Context, data):
    expr, block = data[0], data[1:]
    llvm_loop_header(ctx)
    expr_type = parse_expr(ctx, expr)
    assert expr_type == LLVM.bool
    llvm_loop(ctx)
    parse_block(ctx, block)
    llvm_end_loop(ctx)


def parse_return(ctx: Context, data):
    expr_type = parse_expr(ctx, data)
    assert expr_type == ctx.current_return_type
    llvm_ret(ctx)


def infer_type(_ctx: Context, tag: str, type_0: LLVM.type, type_1: LLVM.type) -> LLVM.type:
    number_type = {LLVM.int, LLVM.float}
    # if tag == "div":
    #     assert type_0 in number_type and type_1 in number_type
    #     return LLVM.float
    if tag in ("sub", "add", "mul", "div", "rem"):
        assert type_0 == type_1 == LLVM.int
        return LLVM.int
    if tag in ("lt", "le", "bt", "be", "eq", "neq"):
        assert type_0 == LLVM.int and type_1 == LLVM.int
        return LLVM.bool
    # if tag in ("sub", "add", "mul"):
    #     assert type_0 in number_type and type_1 in number_type
    #     return LLVM.float if LLVM.float in (type_0, type_1) else LLVM.int


def llvm_system_call(ctx: Context, function_name, params) -> LLVM.type:
    _, params_data = params
    if function_name == "putd":
        assert len(params_data) == 1
        expr_type = parse_expr(ctx, params_data[0])
        assert expr_type == LLVM.int  # or expr_type == LLVM.bool
        llvm_putd(ctx)
        return LLVM.void
    if function_name == "shift":
        assert len(params_data) == 2
        ptr_expression, ident_value = params_data
        ptr_type = parse_expr(ctx, ptr_expression)
        ident_type = parse_expr(ctx, ident_value)
        assert is_pointer(ptr_type) and ident_type == LLVM.int
        shift(ctx)
        return ptr_type
    if function_name == "deref":
        assert len(params_data) == 1
        expr_type = parse_expr(ctx, params_data[0])
        assert is_pointer(expr_type)
        deref_ptr_and_push(ctx)
        return expr_type[:-1]
    if function_name == "addr":
        assert len(params_data) == 1
        tag, data = params_data[0]
        assert tag == VAR, (tag, data)
        ctx.parameters.append(f"%{data}")
        return ctx.variables[data] + "*"
        # assert 0
        # expr_type = parse_expr(ctx, params_data[0])
        # assert expr_type == LLVM.int  # or expr_type == LLVM.bool
    if function_name == "as_p":
        assert len(params_data) == 2
        ptr_expression, assign_value = params_data
        ptr_type = parse_expr(ctx, ptr_expression)
        assign_type = parse_expr(ctx, assign_value)
        assert is_pointer(ptr_type) and assign_type == ptr_type[:-1], (ptr_type, assign_type)
        assign_ptr(ctx)
        return LLVM.void
    if function_name == "array_from":
        create_array_and_push(ctx, LLVM.int, len(params_data))  # ptr ptr + 1
        llvm_duplicate(ctx)
        for param in params_data:
            tag, data = param
            if tag == "unary_minus":
                tag = NUMBER
                data = "-" + data[1]
            assert tag == NUMBER, param
            llvm_duplicate(ctx)
            llvm_push_number(ctx, data)
            assign_ptr(ctx)
            llvm_push_number(ctx, 1)
            shift(ctx)
        llvm_pop(ctx)
        return LLVM.ptr_int
    if function_name == "array":
        assert len(params_data) == 2
        array_type_data, size = params_data
        assert array_type_data[0] == GENERIC_TYPE, array_type_data
        assert size[0] == "number"
        create_array_and_push(ctx, array_type_data[1], size[1])
        return array_type_data[1] + "*"
    assert 0, f"unknown system function {function_name}"


def parse_expr(ctx: Context, data) -> LLVM.type:
    tag, data = data
    if tag == "boolean":
        llvm_push_number(ctx, int(data == "true"))
        return LLVM.bool
    if tag == "number":
        llvm_push_number(ctx, data)
        return LLVM.int
    if tag == "var":
        check_variable_exists(ctx, data)
        variable_type = ctx.variables[data]
        llvm_push_variable(ctx, data, variable_type)
        return ctx.variables[data]
    if tag in ("and", "or"):
        expr_type1 = parse_expr(ctx, data[0])
        expr_type2 = parse_expr(ctx, data[1])
        assert expr_type1 == expr_type2 == LLVM.bool
        reg = ctx.register_counter
        ctx.listing.append(f"%{reg + 1} = trunc i8 {ctx.parameters.pop()} to i1")
        ctx.listing.append(f"%{reg + 2} = trunc i8 {ctx.parameters.pop()} to i1")
        # % 3 = and i1 % first, % second
        ctx.listing.append(f"%{reg + 3} = {tag} i1 %{reg + 1}, {reg + 2}")
        ctx.listing.append(f"%{reg + 4} = zext i1 %{reg + 3} to i8")
        add_register(ctx, 4)
        ctx.parameters.append(ctx.register_counter)
        return LLVM.bool
    if tag in ("sub", "add", "mul", "div", "rem",
               "lt", "le", "bt", "be", "eq", "neq"):
        type_0 = parse_expr(ctx, data[0])
        type_1 = parse_expr(ctx, data[1])
        result_type = infer_type(ctx, tag, type_0, type_1)
        llvm_apply_binary_operation(ctx, tag)
        return result_type
    if tag == "function_call":
        function_name, params = data
        _, params_data = params
        signature = ctx.signatures.get(function_name)
        assert signature is not None, f"unknown function `{function_name}`\n" \
                                      f"known functions are: {list(ctx.signatures.keys())}"
        assert len(signature.parameters) == len(params_data)
        for i, param in enumerate(params_data):
            expr_type = parse_expr(ctx, param)
            assert expr_type == signature.parameters[i]
        llvm_call_function(ctx, function_name)
        return ctx.signatures[function_name].return_type
    if tag == "unary_minus":  # temp
        return parse_expr(ctx, ("sub", [('number', '0'), data]))
    if tag == "neg":
        expr_type = parse_expr(ctx, data)
        assert expr_type == LLVM.bool
        neg(ctx)
        return LLVM.bool
    if tag == "system_call":
        function_name, params = data
        return llvm_system_call(ctx, function_name, params)
    assert 0, f"unknown tag {tag}"


def parse_declare_variable(ctx: Context, data):
    typeof, name, expr = data
    check_variable_doesnt_exist(ctx, name)
    ctx.variables[name] = typeof
    llvm_declare(ctx, name, typeof)
    expr_type = parse_expr(ctx, expr)
    assert expr_type == typeof, (expr_type, typeof, name)
    llvm_assign(ctx, name, typeof)
    # typeof use


def parse_assign_variable(ctx: Context, data):
    name, expr = data
    expr_type = parse_expr(ctx, expr)
    check_variable_exists(ctx, name)
    assert expr_type == ctx.variables[name]
    llvm_assign(ctx, name, expr_type)


def parse_statement(ctx: Context, statement):
    if statement == "return_void":
        llvm_ret_void(ctx)
        return
    tag, data = statement
    if tag == "if":
        parse_if(ctx, data)
    elif tag == "return":
        parse_return(ctx, data)
    elif tag == "expression":
        expr_type = parse_expr(ctx, data)
        if expr_type != LLVM.void:
            llvm_pop(ctx)
    elif tag == "while":
        parse_while(ctx, data)
    elif tag == "declare_variable":
        parse_declare_variable(ctx, data)
    elif tag == "assigment":
        parse_assign_variable(ctx, data)
    else:
        assert 0, f"Unhandled tag {tag}"
