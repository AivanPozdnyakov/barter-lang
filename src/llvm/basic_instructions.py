from src.llvm.help import *
from src.llvm.struct import FunctionSignature


def declare(ctx: Context, variable_name: str) -> None:
    check_variable_name(variable_name)
    check_variable_doesnt_exist(ctx, variable_name)
    ctx.variables.add(variable_name)
    ctx.listing.append(f"%{variable_name} = alloca i32")


def assign(ctx: Context, variable_name: str) -> None:
    check_variable_name(variable_name)
    check_variable_exists(ctx, variable_name)
    assigned_value = ctx.parameters.pop()
    listing = f"store i32 {assigned_value}, i32* %{variable_name}"
    ctx.listing.append(listing)


def push_variable(ctx: Context, variable_name: str) -> None:
    check_variable_exists(ctx, variable_name)
    register_counter = add_register(ctx)
    ctx.listing.append(f"%{register_counter} = load i32, i32* %{variable_name}")
    ctx.parameters.append(f"%{register_counter}")


def push_number(ctx: Context, number: int) -> None:
    ctx.parameters.append(str(number))


def apply_binary_operation(ctx: Context, operation_type: str) -> None:
    arithmetic_operations = {"add": "add", "sub": "sub", "mul": "mul", "div": "sdiv"}
    logical_operations = {"lt": "slt", "<=": "sle", "be": "sge", ">": "sgt", "==": "eq", "!=": "ne"}
    # ("sub", "add", "mul", "div", "lt")
    # arithmetic_operations = {"+": "add", "-": "sub", "*": "mul", "/": "sdiv"}
    # logical_operations = {"<": "slt", "<=": "sle", ">=": "sge", ">": "sgt", "==": "eq", "!=": "ne"}
    # assert len(ctx.parameters) == 2, f"wrong number of arguments for binary_operation `{operation_type}:\n" \
    #                                  f"\texpected 2, got {len(ctx.parameters)}"
    params = ctx.parameters[-2:]
    assert len(params) == 2, (operation_type, ctx.parameters)
    parameters_as_str = ",".join(params)
    register_counter = add_register(ctx)
    if operation_type in arithmetic_operations:
        operator = arithmetic_operations[operation_type]
        listing = f"%{register_counter} = {operator} i32 {parameters_as_str}"
    elif operation_type in logical_operations:
        operator = logical_operations[operation_type]
        listing = f"%{register_counter} = icmp {operator} i32 {parameters_as_str}"
        register_counter = add_register(ctx)
        listing += f"\n%{register_counter} = zext i1 %{register_counter - 1} to i32"
    else:
        assert False, f"unknown operation type `{operation_type} for binary"
    ctx.listing.append(listing)
    for _ in range(2):
        ctx.parameters.pop()
    ctx.parameters.append(f"%{register_counter}")


def call_function(ctx: Context, function_name: str) -> None:
    signature = ctx.signatures.get(function_name)
    assert signature is not None, f"unknown function `{function_name}`\n" \
                                  f"known functions are: {list(ctx.signatures.keys())}"
    expected = signature.number_of_parameters
    parameters_as_str = ",".join([f"i32 {param}" for param in ctx.parameters[-expected:]])
    # parameters_as_str = f"i32 {ctx.parameters.pop()}"
    register_counter = add_register(ctx)
    ctx.listing.append(f"%{register_counter} = call i32 @{function_name}({parameters_as_str})")
    for i in range(expected):
        ctx.parameters.pop()
    ctx.parameters.append(f"%{register_counter}")


def duplicate(ctx: Context) -> None:
    ctx.parameters.append(ctx.parameters[-1])


def pop(ctx: Context) -> None:
    ctx.parameters.pop()


def function(ctx: Context, function_name: str, params: list[tuple[str, str]], return_type: str) -> None:
    ctx.signatures[function_name] = FunctionSignature(len(params))

    params_as_str = ",".join([param[0] for param in params])
    ctx.listing.append(f"define {return_type} @{function_name}({params_as_str}){{")
    for i, param in enumerate(params):
        typeof, name = param
        declare(ctx, name)
        ctx.parameters.append(f"%{i}")
        assign(ctx, name)
    add_register(ctx, len(params))
    # map them into registers...


def end_function(ctx: Context) -> None:
    print(ctx.parameters)
    ctx.parameters = []
    ctx.register_counter = 0
    ctx.listing.append("}")


def ret(ctx: Context) -> None:
    ctx.listing.append(f"ret i32 {ctx.parameters.pop()}")
