from src.data_structure import Context
from src.help import add_register
from src.llvm.basic_instruction import llvm_assign


def llvm_ret_void(ctx: Context) -> None:
    ctx.return_index.append(len(ctx.listing))
    ctx.listing.append(f"br label TMP")


def llvm_ret(ctx: Context) -> None:
    llvm_assign(ctx, "return", ctx.current_return_type)
    llvm_ret_void(ctx)


def llvm_branch(ctx: Context) -> None:
    parameters = ctx.parameters
    register_counter = add_register(ctx)
    # "%5 = trunc i8 %4 to i1"

    # condition = f"eq i32 {parameters.pop()}, 1"
    # listing = f"""%{register_counter} = icmp {condition}
    listing = f"""%{register_counter} = trunc i8 {parameters.pop()} to i1
br i1 %{register_counter}, label %{register_counter + 1}, label TMP
{register_counter + 1}:"""
    add_register(ctx)
    ctx.branch_temp_indexes.append(len(ctx.listing))
    ctx.listing.append(listing)


def is_branch(s: str) -> bool:
    return s.startswith("br label")


def llvm_branch_end(ctx: Context) -> None:
    label = add_register(ctx)
    last_branch_index = ctx.branch_temp_indexes.pop()
    ctx.listing[last_branch_index] = ctx.listing[last_branch_index].replace("TMP", f"%{label}")
    if not is_branch(ctx.listing[-1]):
        ctx.listing.append(f"br label %{label}")
    ctx.listing.append(f"{label}:")


def llvm_loop_header(ctx: Context) -> None:
    register_counter = add_register(ctx)
    ctx.loop_labels.append(str(register_counter))
    ctx.listing.append(f"""br label %{register_counter}
{register_counter}:""")


def llvm_loop(ctx: Context) -> None:
    "trunc i8 {parameters.pop()} to i1"
    register_counter = ctx.register_counter
    listing = f"""%{register_counter + 1} = trunc i8 {ctx.parameters.pop()} to i1
br i1 %{register_counter + 1}, label %{register_counter + 2}, label TMP
{register_counter + 2}:"""
    ctx.register_counter = register_counter + 2
    ctx.loop_temp_indexes.append(len(ctx.listing))
    ctx.listing.append(listing)


def llvm_end_loop(ctx: Context) -> None:
    after_label = add_register(ctx)
    before_label = ctx.loop_labels.pop()
    last_loop_index = ctx.loop_temp_indexes.pop()
    ctx.listing[last_loop_index] = ctx.listing[last_loop_index].replace("TMP", f"%{after_label}")
    if not is_branch(ctx.listing[-1]):
        ctx.listing.append(f"br label %{before_label}")
    ctx.listing.append(f"{after_label}:")
