from src.llvm.help import *

# def declare_ptr(ctx: Context, ptr_name: str) -> None:
#     check_variable_name(ptr_name)
#     check_variable_doesnt_exist(ctx, ptr_name)
#     ctx.variables.add(ptr_name)
#     ctx.listing.append(f"%{ptr_name} = alloca i32*")
from src.llvm.struct import LLVM


def reference_ptr(ctx: Context, ptr_name: str, variable_name: str) -> None:
    # store i32* %2, i32** %3 ;, align 8    ;ptr = &a
    ctx.listing.append(f"store i32* %{variable_name}, i32** %{ptr_name}")


def reference_ptr_to_top_of_the_stack_experimental(ctx: Context, ptr_name: str) -> None:
    top_of_the_stack = ctx.parameters.pop()
    # store i32* %2, i32** %3 ;, align 8    ;ptr = &a
    ctx.listing.append(f"store i32* {top_of_the_stack}, i32** %{ptr_name}")


def assign_ptr(ctx: Context) -> None:
    # register_counter = load_ptr(ctx, ptr_name)
    assigned_value = ctx.parameters.pop()
    ptr_name = ctx.parameters.pop()
    ctx.listing.append(f"store i32 {assigned_value}, i32* {ptr_name}")


def deref_ptr_and_push(ctx: Context) -> None:
    # %4 = load i32*, i32** %2, align 8     ;load ptr
    # %5 = load i32, i32* %4, align 4       ;*ptr
    ptr_name = ctx.parameters.pop()
    register_counter = add_register(ctx)
    ctx.listing.append(f"%{register_counter} = load i32, i32* {ptr_name}")
    ctx.parameters.append(f"%{register_counter}")


def shift(ctx: Context) -> None:
    # %5 = load i32*, i32** %3 ;, align 8           ;*ptr
    # %6 = getelementptr inbounds i32, i32* %5, i32 1
    # ;ptr+1
    # register_counter = load_ptr(ctx, ptr_name)
    register_counter = add_register(ctx)
    indent_value = ctx.parameters.pop()
    ptr_name = ctx.parameters.pop()
    ctx.listing.append(
        f"%{register_counter} = getelementptr inbounds i32, i32* {ptr_name}, i32 {indent_value}")
    ctx.parameters.append(f"%{register_counter}")


def create_array_and_push(ctx: Context, el_type: LLVM.type, size: int) -> None:
    register_counter = add_register(ctx)
    ctx.listing.append(f"%{register_counter} = alloca [{size} x {el_type}]")
    listing = f"%{register_counter + 1} = getelementptr inbounds [{size} x {el_type}], [{size} x {el_type}]* %{register_counter}, i64 0, i64 0"
    ctx.listing.append(listing)
    register_counter = add_register(ctx)
    ctx.parameters.append(f"%{register_counter}")
    #   %1 = alloca [5 x i32], align 16                                       ;int foo[5];
    #   %2 = alloca i32*, align 8                                             ;int * ptr;
    #   %3 = getelementptr inbounds [5 x i32], [5 x i32]* %1, i64 0, i64 0    ;foo[0]
    #   store i32* %3, i32** %2, align 8                                      ;ptr = foo;
    #   %4 = getelementptr inbounds [5 x i32], [5 x i32]* %1, i64 0, i64 0    ;foo[0]
    #   store i32 1, i32* %4, align 16                                        ;foo[0] = 1
    #   %5 = load i32*, i32** %2, align 8                                     ;
    #   %6 = getelementptr inbounds i32, i32* %5, i64 1
    #   store i32 2, i32* %6, align 4
