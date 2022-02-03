import uuid

from src.llvm.struct import Context


def check_variable_name(variable_name: str):
    assert 0, "depreceated"
    pass


def is_pointer(s: str) -> bool:
    return s.endswith("*")

specials = {"return", "if", "while", "macro", "func", "for", "else", "elseif", "end",
            "int", "i32", "float", "double", "f32", "bool",
            "true", "false"}

def check_variable_doesnt_exist(ctx: Context, variable_name: str):
    assert variable_name not in ctx.variables and variable_name not in specials, variable_name

def check_variable_exists(ctx: Context, variable_name: str):
    assert variable_name in ctx.variables, variable_name


def add_register(ctx: Context, n=1) -> int:
    ctx.register_counter += n
    return ctx.register_counter


def get_random_name() -> str:
    return uuid.uuid4().hex


def f_res(path: str) -> str:
    return "../res/" + path


def f_build(path: str) -> str:
    return "../build/" + path
