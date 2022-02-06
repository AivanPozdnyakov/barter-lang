def infer_type(_ctx: Context, tag: str, type_0: BarterType, type_1: BarterType) -> BarterType:
    if tag in ("sub", "add", "mul", "div", "rem"):
        assert type_0 == type_1 == "bint"
        return "bint"
    if tag in ("lt", "le", "bt", "be"):
        assert type_0 == "bint" == type_1
        return "bbool"


def parse_expr(ctx: Context, data) -> BarterType:
    tag, data = data
    if tag == "boolean":
        llvm_push_number(ctx, int(data == "true"))
        return "bbool"
    if tag == "number":
        llvm_push_number(ctx, data)
        return "bint"
    if tag == "var":
        check_variable_exists(ctx, data)
        variable_type = ctx.variables[data]
        llvm_push_variable(ctx, data, variable_type)
        return ctx.variables[data]
    if tag in ("and", "or"):
        expr_type1 = parse_expr(ctx, data[0])
        expr_type2 = parse_expr(ctx, data[1])
        assert expr_type1 == expr_type2 == "bbool"
        reg = ctx.register_counter
        ctx.listing.append(f"%{reg + 1} = trunc i8 {ctx.parameters.pop()} to i1")
        ctx.listing.append(f"%{reg + 2} = trunc i8 {ctx.parameters.pop()} to i1")
        # % 3 = and i1 % first, % second
        ctx.listing.append(f"%{reg + 3} = {tag} i1 %{reg + 1}, %{reg + 2}")
        ctx.listing.append(f"%{reg + 4} = zext i1 %{reg + 3} to i8")
        ctx.parameters.append(f"%{add_register(ctx, 4)}")
        return "bbool"
    if tag in ("sub", "add", "mul", "div", "rem",
               "lt", "le", "bt", "be"):
        type_0 = parse_expr(ctx, data[0])
        type_1 = parse_expr(ctx, data[1])
        result_type = infer_type(ctx, tag, type_0, type_1)
        llvm_apply_binary_operation(ctx, tag)
        return result_type
    if tag in ("eq", "ne"):
        type_0 = parse_expr(ctx, data[0])
        type_1 = parse_expr(ctx, data[1])
        assert type_0 == type_1
        llvm_apply_eq_check(ctx, tag, type_0)
        return "bbool"
    if tag == "function_call":
        function_name, params = data
        _, params_data = params
        signature = ctx.signatures.get(function_name)
        assert signature is not None, f"unknown function `{function_name}`\n" \
                                      f"known functions are: {list(ctx.signatures.keys())}"
        assert len(signature.parameters) == len(params_data)
        for i, param in enumerate(params_data):
            expr_type = parse_expr(ctx, param)
            assert expr_type == signature.parameters[i], (expr_type, signature.parameters[i])
        llvm_call_function(ctx, function_name)
        return ctx.signatures[function_name].return_type
    if tag == "unary_minus":  # temp
        return parse_expr(ctx, ("sub", [('number', '0'), data]))
    if tag == "neg":
        expr_type = parse_expr(ctx, data)
        assert expr_type == "bbool"
        neg(ctx)
        return "bbool"
    if tag == "system_call":
        function_name, params = data
        return llvm_system_call(ctx, function_name, params)
    assert 0, f"unknown tag {tag}"
