import os
import shutil
import subprocess

import click

from src.llvm.brand_compiler import finalize_llvm
from src.llvm.help import build_ctx, Timeit
from src.communication_layer import parse_ast
from src.syntax_tree import build_ast_from_file, build_ast


# @click.command()
@click.option("--clean", "-c", is_flag=True)
@click.option("--build", "-b", is_flag=True)
@click.option("--timeit", "-t", is_flag=True)
@click.option("--llvm_only", is_flag=True)  
@click.option("--optimize", "-O", type=int, default=0)
@click.option("--output", "-o")
@click.argument("file_path", type=click.Path(exists=True))
@click.argument("deps", nargs=-1, type=click.Path(exists=True))
def main(
    file_path: str,
    clean: bool = False,
    build: bool = False,
    llvm_only: bool = False,
    optimize: int = 0,
    output: str = None,
    deps: list[str] = None,
    timeit: bool = False,
):
    assert not llvm_only, "this option is not yet supported"
    assert not (clean and build), "`clean` and `build` options are mutually exclusive"
    assert 0 <= optimize <= 3, "optimize level must be between 0 and 3 inclusive"
    assert output is None or output.endswith(".exe")
    if deps is None:
        deps = []
    if output is not None:
        output_directory_path = os.path.dirname(output)
        llvm_filename = os.path.basename(output).replace('.exe', '.ll')
    else:
        output_directory_path = os.path.join(os.path.dirname(file_path), "junk")
        llvm_filename = os.path.basename(file_path).replace('.barter', '.ll')
    llvm_path = os.path.join(output_directory_path, llvm_filename)
    output = output or llvm_path.replace(".ll", ".exe")
    rules_filename = os.path.dirname(os.path.realpath(__file__)) + "/bl_lexer_rules.txt"
    if len(output_directory_path):
        os.makedirs(output_directory_path, exist_ok=True)
    with Timeit("Llvm file generation took", not timeit):
        ctx = build_ctx()
        with open(rules_filename, "r") as rules:
            with open(file_path, "r") as code:
                ast = build_ast(rules.read(), code.read())
        parse_ast(ctx, ast)
        llvm = finalize_llvm(ctx)
        with open(llvm_path, "w") as f:
            f.write(llvm)
    with Timeit("Clang build took", not timeit):
        # build_res = subprocess.run(
        #     f"clang -o {output} {llvm_path} {''.join(deps)}", capture_output=True, encoding="cp866"
        # )
        build_res = subprocess.run(f"clang -O{optimize} -o {output} {llvm_path} {''.join(deps)}", capture_output=True, encoding="cp866")
        assert build_res.returncode == 0, build_res
    if not build:
        with Timeit("Execution took", not timeit):
            run_res = subprocess.call(output)
            print(f"\nExited with code {run_res}")
    if clean:
        shutil.rmtree(output_directory_path)


if __name__ == "__main__":
    # print("current_directory", os.getcwd())
    # print("script path", os.path.realpath(__file__))
    # print("script path directory", os.path.dirname(os.path.realpath(__file__)))
    # print("rules path", os.path.join(os.path.dirname(os.path.realpath(__file__)), "bl_lexer_rules.txt"))
    # print("script name", os.path.basename(os.path.realpath(__file__)))
    main("res/for_test/struct.barter")