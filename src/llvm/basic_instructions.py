from src.llvm.help import *
from src.llvm.struct import LLVM


def llvm_declare(ctx: Context, variable_name: str, variable_type: LLVM.type) -> None:
    ctx.listing.append(f"%{variable_name} = alloca {variable_type}")
    # ctx.listing.append(f"%{variable_name} = alloca i32")


def llvm_assign(ctx: Context, variable_name: str, variable_type: LLVM.type) -> None:
    assigned_value = ctx.parameters.pop()
    # listing = f"store i32 {assigned_value}, i32* %{variable_name}"
    listing = f"store {variable_type} {assigned_value}, {variable_type}* %{variable_name}"
    ctx.listing.append(listing)


def llvm_push_variable(ctx: Context, variable_name: str, variable_type: LLVM.type) -> None:
    register_counter = add_register(ctx)
    ctx.listing.append(f"%{register_counter} = load {variable_type}, {variable_type}* %{variable_name}")
    # ctx.listing.append(f"%{register_counter} = load i32, i32* %{variable_name}")
    ctx.parameters.append(f"%{register_counter}")


def llvm_push_number(ctx: Context, number: int) -> None:
    ctx.parameters.append(str(number))


def llvm_apply_binary_operation(ctx: Context, operation_type: str) -> None:
    arithmetic_operations = {"add": "add", "sub": "sub", "mul": "mul", "div": "sdiv", "rem": "srem"}
    logical_operations = {"lt": "slt", "le": "sle", "be": "sge", "bt": "sgt", "eq": "eq", "neq": "ne"}
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
        listing += f"\n%{register_counter} = zext i1 %{register_counter - 1} to i8"
    else:
        assert False, f"unknown operation type `{operation_type} for binary"
    ctx.listing.append(listing)
    for _ in range(2):
        llvm_pop(ctx)
    ctx.parameters.append(f"%{register_counter}")


def llvm_call_function(ctx: Context, function_name: str) -> None:
    signature = ctx.signatures.get(function_name)
    parameters = []
    for i, typeof in enumerate(signature.parameters):
        param = ctx.parameters.pop()
        parameters.append(f"{typeof} {param}")
    parameters_as_str = ",".join(reversed(parameters))
    pre = ""
    if signature.return_type != LLVM.void:
        pre = f"%{add_register(ctx)} = "
        ctx.parameters.append(f"%{ctx.register_counter}")
    ctx.listing.append(f"{pre}call {signature.return_type} @{function_name}({parameters_as_str})")


def llvm_duplicate(ctx: Context) -> None:
    ctx.parameters.append(ctx.parameters[-1])


def llvm_pop(ctx: Context) -> str:
    return ctx.parameters.pop()


def llvm_end_function(ctx: Context) -> None:
    label = add_register(ctx)
    for i in ctx.return_index:
        ctx.listing[i] = ctx.listing[i].replace("TMP", f"%{label}")
    ctx.listing.append(f"{label}:")
    if ctx.current_return_type != LLVM.void:
        llvm_push_variable(ctx, "return", ctx.current_return_type)
    listing = f"ret {ctx.current_return_type} {ctx.parameters.pop() if ctx.current_return_type != LLVM.void else ''}"
    ctx.listing.append(listing)
    ctx.clear()
    ctx.listing.append("}")


def llvm_putd(ctx: Context) -> None:
    listing = f"%{add_register(ctx)} = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([3 x i8], [3 x i8] * @0, i32 0, i32 0), " \
              f"i32 {ctx.parameters.pop()})"
    ctx.listing.append(listing)


def neg(ctx: Context) -> None:
    reg = ctx.register_counter
    ctx.listing.append(f"%{reg + 1} = trunc i8 {ctx.parameters.pop()} to i1")
    ctx.listing.append(f"%{reg + 2} = xor i1 %{reg + 1}, true")
    ctx.listing.append(f"%{reg + 3} = zext i1 %{reg + 2} to i8")
    add_register(ctx, 3)
    ctx.parameters.append(f"%{ctx.register_counter}")
