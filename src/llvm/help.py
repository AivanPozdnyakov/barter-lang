import time
import uuid

import rich

from src.llvm.struct import Context


def is_pointer(s: str) -> bool:
    return s.endswith("*")


specials = {"return", "if", "while", "macro", "func", "for", "else", "elseif", "end",
            "int", "i32", "float", "double", "f32", "bool",
            "true", "false"}


def check_variable_doesnt_exist(ctx: Context, variable_name: str):
    assert variable_name not in ctx.variables and variable_name not in specials, variable_name


def check_variable_exists(ctx: Context, variable_name: str):
    assert variable_name in ctx.variables, variable_name


def build_ctx() -> Context:
    # putchar_signature = FunctionSignature([LLVM.int], LLVM.void)
    # signatures = {"printf": FunctionSignature([LLVM.ptr_byte, LLVM.int], LLVM.int)}
    # signatures = {"putd": SysSignature([LLVM.int], LLVM.void), "addr": SysSignature(['VAR'], LLVM.ptrvoid)}
    ctx = Context()
    return ctx


def add_register(ctx: Context, n=1) -> int:
    ctx.register_counter += n
    return ctx.register_counter


def get_random_name() -> str:
    return uuid.uuid4().hex


def f_res(path: str) -> str:
    return "res/" + path


def f_build(path: str) -> str:
    return "build/" + path

class Timeit:
    def __init__(self, message, silent=False):
        self.message = message
        self.elapsed = 0
        self.silent = silent

    def __enter__(self):
        self.elapsed = time.time()
        return self

    def __exit__(self, typeof, value, traceback):
        self.elapsed = time.time() - self.elapsed
        if not self.silent:
                rich.print(f"[cyan]{self.message} {self.elapsed}[/cyan]")
