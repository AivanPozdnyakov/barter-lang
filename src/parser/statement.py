def parse_block(ctx: Context, body):
    for statement in body:
        parse_statement(ctx, statement)


def parse_if(ctx: Context, data):
    expr, block = data[0], data[1:]
    expr_type = parse_expr(ctx, expr)
    assert expr_type == "bbool", expr_type
    llvm_branch(ctx)
    parse_block(ctx, block)
    llvm_branch_end(ctx)


def parse_while(ctx: Context, data):
    expr, block = data[0], data[1:]
    llvm_loop_header(ctx)
    expr_type = parse_expr(ctx, expr)
    assert expr_type == "bbool"
    llvm_loop(ctx)
    parse_block(ctx, block)
    llvm_end_loop(ctx)


def parse_declare_variable(ctx: Context, data):
    typeof, name, expr = data
    check_variable_doesnt_exist(ctx, name)
    ctx.variables[name] = typeof
    llvm_declare(ctx, name, typeof)
    expr_type = parse_expr(ctx, expr)
    assert expr_type == typeof, (expr_type, typeof, name)
    llvm_assign(ctx, name, typeof)


def parse_assign_variable(ctx: Context, data):
    name, expr = data
    expr_type = parse_expr(ctx, expr)
    check_variable_exists(ctx, name)
    assert expr_type == ctx.variables[name]
    llvm_assign(ctx, name, expr_type)


def parse_statement(ctx: Context, statement):
    if statement == "return_void":
        llvm_ret_void(ctx)
        return
    tag, data = statement
    if tag == "if":
        parse_if(ctx, data)
    elif tag == "return":
        parse_return(ctx, data)
    elif tag == "expression":
        expr_type = parse_expr(ctx, data)
        if expr_type != LLVM.void:
            llvm_pop(ctx)
    elif tag == "while":
        parse_while(ctx, data)
    elif tag == "declare_variable":
        parse_declare_variable(ctx, data)
    elif tag == "assigment":
        parse_assign_variable(ctx, data)
    else:
        assert 0, f"Unhandled tag {tag}"


def parse_return(ctx: Context, data):
    expr_type = parse_expr(ctx, data)
    assert expr_type == ctx.current_return_type
    llvm_ret(ctx)
