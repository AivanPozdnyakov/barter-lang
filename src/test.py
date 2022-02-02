import subprocess
import time

from barter_test import eq, run_all_tests, scope, echo

from src.ast import build_ast_from_file
from src.llvm.brand_compiler import build_exe_from_llvm, run_executive, finalize_llvm, clean
from src.llvm.help import f_build, f_res
from src.llvm.struct import FunctionSignature, Context, LLVM
from src.llvm_backend import parse_ast


def build_ctx() -> Context:
    putchar_signature = FunctionSignature([LLVM.int], LLVM.void)
    signatures = {"putchar": putchar_signature}
    ctx = Context(signatures=signatures)
    return ctx


def run_to_s(run: subprocess.CompletedProcess) -> str:
    warnings = run.stderr.strip()
    output = run.stdout.strip()
    result = []
    if len(warnings):
        result.append(f"warnings: {warnings}")
    if len(output):
        result.append(f"output: {output}")
    return "; ".join(result)


class TimedScope(scope):
    def __init__(self, name):
        super().__init__(name)
        self.elapsed = 0

    def setup(self):
        self.elapsed = time.time()
        return self

    def close(self):
        self.elapsed = time.time() - self.elapsed


test_cases = {
    "fib": "1346269",
    "return": "-101",
    "putd": "1-1100",
    "void_return": "5",
    "bool": "10",
    "loop": "012345",
    "args_pass": "151",
    "gcd": "55",
    "int_operations": "4 -2 0 7 1 2 -1 6 0 9 1 30".replace(" ", "")
}


def test_all():
    for key, expected in test_cases.items():
        with scope(key):
            ctx = build_ctx()
            ast = build_ast_from_file(f_res(f"for_test/{key}.barter"))
            parse_ast(ctx, ast)
            llvm = finalize_llvm(ctx)
            build_res = build_exe_from_llvm(llvm=llvm, output_filename=f_build(f"{key}.exe"))
            eq(build_res.returncode, 0, f"build_res: {run_to_s(build_res)}")
            run_res = run_executive(path=f_build(f"{key}.exe"))
            eq(run_res.returncode, 0, f"run_res: {run_to_s(run_res)}")
            eq(run_res.stdout, expected)
            clean(suffixes=["exe"])


def _test_all_with_time():
    for key, expected in test_cases.items():
        with scope(key):
            with TimedScope("generating llvm") as s:
                ctx = build_ctx()
                ast = build_ast_from_file(f_res(f"for_test/{key}.barter"))
                parse_ast(ctx, ast)
                llvm = finalize_llvm(ctx)
            echo(f"\t{s.elapsed}")
            with TimedScope("building executable") as s:
                build_res = build_exe_from_llvm(llvm=llvm, output_filename=f_build(f"{key}.exe"))
                eq(build_res.returncode, 0, f"build_res: {run_to_s(build_res)}")
            echo(f"\t{s.elapsed}")
            with TimedScope("execution") as s:
                run_res = run_executive(path=f_build(f"{key}.exe"))
                eq(run_res.returncode, 0, f"run_res: {run_to_s(run_res)}")
                eq(run_res.stdout, expected)
            echo(f"\t{s.elapsed}")
            clean(suffixes=["exe"])


def main() -> None:
    f = time.time()
    run_all_tests()
    elapsed = time.time() - f
    print(f"overall: {elapsed}, per program: {elapsed / len(test_cases)}")


if __name__ == '__main__':
    main()