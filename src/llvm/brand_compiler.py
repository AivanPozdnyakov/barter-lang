import subprocess

from src.llvm.help import f_build, get_random_name
from src.llvm.struct import *


def build_cpp_to_llvm(cpp: str = None, cpp_path: str = None,
                      output_filename: str = None, optimization: str = None) -> subprocess.CompletedProcess:
    if output_filename is None:
        output_filename = f_build("generated.ll")
    # clang -S -emit-llvm res/try.cpp -o output/array.ll
    assert cpp != cpp_path
    if cpp is not None:
        cpp_path = f_build(get_random_name()) + ".cpp"
        with open(cpp_path, "w") as f:
            f.write(cpp)
        return subprocess.run(f"clang {optimization} -S -emit-llvm {cpp_path} -o {output_filename}", capture_output=True,
                              encoding='cp866')
    if cpp_path is not None:
        return subprocess.run(f"clang {optimization} -S -emit-llvm {cpp_path} -o {output_filename}", capture_output=True,
                              encoding='cp866')


def build_exe_from_llvm(llvm: str = None, llvm_path: str = None,
                        output_filename: str = None) -> subprocess.CompletedProcess:
    if output_filename is None:
        llvm_temp = f_build(get_random_name() + ".ll")
        output_filename = f_build("generated.exe")
    else:
        llvm_temp = output_filename.replace(".exe", ".ll")
    assert llvm != llvm_path
    if llvm is not None:
        llvm_path = llvm_temp
        with open(llvm_path, "w") as f:
            f.write(llvm)
        return subprocess.run(f"clang {llvm_path} -o {output_filename}", capture_output=True, encoding='cp866')
    if llvm_path is not None:
        return subprocess.run(f"clang {llvm_path} -o {output_filename}", capture_output=True, encoding='cp866')


def run_executive(path: str = None) -> subprocess.CompletedProcess:
    if path is None:
        path = f_build("generated.exe")
    return subprocess.run(f"{path}", capture_output=True, encoding='cp866')


def clean(path: str = None, suffixes: list[str] = None) -> None:
    path = path or f_build("")
    if suffixes is None:
        suffixes = ["exe", "ll"]
    for suf in suffixes:
        run = subprocess.run(f'bash -c "rm -rf {path}*.{suf}"', shell=True, capture_output=True, encoding="cp866",
                             check=True)
        # print(run)


def finalize_llvm(ctx: Context) -> str:
    header = """target triple = "x86_64-pc-windows-msvc19.31.30818"

@0 = private unnamed_addr constant [3 x i8] c"%d\00", align 1
declare i32 @printf(i8*, ...)

"""
    return header + "\n".join(ctx.listing)
