from src.llvm.help import *


def branch(ctx: Context) -> None:
    parameters = ctx.parameters
    register_counter = add_register(ctx)
    condition = f"eq i32 {parameters.pop()}, 1"
    listing = f"""%{register_counter} = icmp {condition}
br i1 %{register_counter}, label %{register_counter + 1}, label TMP
{register_counter + 1}:"""
    add_register(ctx)
    ctx.branch_temp_indexes.append(len(ctx.listing))
    ctx.listing.append(listing)


def end_branch(ctx: Context) -> None:
    label = add_register(ctx)
    last_branch_index = ctx.branch_temp_indexes.pop()
    ctx.listing[last_branch_index] = ctx.listing[last_branch_index].replace("TMP", f"%{label}")
    ctx.listing.append(f"br label %{label}")
    ctx.listing.append(f"{label}:")


def loop_header(ctx: Context) -> None:
    register_counter = add_register(ctx)
    ctx.loop_labels.append(str(register_counter))
    ctx.listing.append(f"""br label %{register_counter}
{register_counter}:""")


def loop(ctx: Context) -> None:
    condition = f"ne i32 {ctx.parameters.pop()}, 0"
    register_counter = ctx.register_counter
    listing = f"""%{register_counter + 1} = icmp {condition}
br i1 %{register_counter + 1}, label %{register_counter + 2}, label TMP
{register_counter + 2}:"""
    ctx.register_counter = register_counter + 2
    ctx.loop_temp_indexes.append(len(ctx.listing))
    ctx.listing.append(listing)


def end_loop(ctx: Context) -> None:
    after_label = add_register(ctx)
    before_label = ctx.loop_labels.pop()
    last_loop_index = ctx.loop_temp_indexes.pop()
    ctx.listing[last_loop_index] = ctx.listing[last_loop_index].replace("TMP", f"%{after_label}")
    ctx.listing.append(f"br label %{before_label}")
    ctx.listing.append(f"{after_label}:")
