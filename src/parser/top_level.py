from src.data_structure import FunctionSignature, StructType, BarterType
from src.help import check_variable_doesnt_exist
from src.llvm.control_flow_instructions import *


def parse_importc(ctx: Context, data) -> None:
    name, params, return_type = data
    ctx.signatures[name] = FunctionSignature(params[1], return_type)
    params = ",".join(params[1])
    ctx.listing.append(f"declare {return_type} @{name}({params})")


def parse_struct(ctx: Context, data) -> None:
    name, params = data
    check_variable_doesnt_exist(ctx)
    params = [param for _, param in params[1]]
    params_type = [typeof for typeof, name in params]
    ctx.listing.append(f"%struct.{name} = type {{ {','.join(params_type)} }}")
    ctx.structs[name] = StructType(params)


#   %struct.A = type { i32, float, i32 }                                    ; declare
#   %2 = alloca %struct.A, align 4                                          ; allocate
#   %3 = getelementptr inbounds %struct.A, %struct.A* %1, i32 0, i32 0      ; x
#   store i32 1, i32* %3, align 4
#   %4 = getelementptr inbounds %struct.A, %struct.A* %1, i32 0, i32 2      ; z


def parse_ast(ctx: Context, ast) -> None:
    for f in ast:
        tag, data = f
        if tag == "function":
            parse_function(ctx, data)
        elif tag == "importc":
            parse_importc(ctx, data)
        elif tag == "struct":
            parse_struct(ctx, data)
        else:
            assert 0, f"Unhandled tag {tag}"




def finalize_llvm(ctx: Context) -> str:
    header = """target triple = "x86_64-pc-windows-msvc19.31.30818"

@0 = private unnamed_addr constant [3 x i8] c"%d\00"        ; for putd
declare i32 @printf(i8*, ...)                               ; can't have varadic functions just for now

"""
    return header + "\n".join(ctx.listing)
