from src.llvm.struct import Context


def check_variable_name(variable_name: str):
    pass


def check_variable_doesnt_exist(ctx: Context, variable_name: str):
    pass


def check_variable_exists(ctx: Context, variable_name: str):
    pass


def add_register(ctx: Context, n=1) -> int:
    ctx.register_counter += n
    return ctx.register_counter
