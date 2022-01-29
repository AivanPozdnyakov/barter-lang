import os
import subprocess
from collections import Callable

from src.llvm.basic_instructions import *
from src.llvm.control_flow_instructions import *
from src.llvm.ptr_instructions import *
from src.llvm.struct import *


def generate_llvm(ctx: Context) -> str:
    header = """target triple = "x86_64-pc-windows-msvc19.31.30818"
        
declare i32 @putchar(i32)

"""
    return header + "\n".join(ctx.listing)


def run_llvm(llvm, silent=False) -> str:
    with open("../build/generated_llvm.ll", "w") as f:
        f.write(llvm)
    silent and print("clang is working...")
    os.system("clang -o ../build/generated.exe ../build/generated_llvm.ll")
    silent and print("clang is done.")
    silent and print("-" * 20)
    res = subprocess.run("../build/generated.exe", capture_output=True)
    return res.stdout.decode("utf-8")
    # os.system(r".\output\generated.exe")


def build(instructions: Callable) -> str:
    putchar_signature = FunctionSignature(1)
    signatures = {"putchar": putchar_signature}
    ctx = Context(signatures=signatures)
    print("llvm is generating...")
    instructions()
    print("done generating llvm")
    return run_llvm(generate_llvm(ctx))
