def llvm_system_call(ctx: Context, function_name, params) -> BarterType:
    _, params_data = params
    if function_name == "printf":
        ptr = params_data[0]
        if len(params_data) == 1:
            other = []
        else:
            other = params_data[1:]
        ptr_type = parse_expr(ctx, ptr)
        assert ptr_type == "bbyte*"
        ptr_itself = llvm_pop(ctx)
        rest = []
        for param in other:
            expr_type = parse_expr(ctx, param)
            assert expr_type == "bint"
            rest.append(llvm_pop(ctx))
        ctx.listing.append(f"%{add_register(ctx)} = call i32 (i8*, ...) @printf(i8* {ptr_itself})")
        return "bvoid"
    if function_name == "putd":
        assert len(params_data) == 1
        expr_type = parse_expr(ctx, params_data[0])
        assert expr_type == "bint"  # or expr_type == LLVM.bool
        llvm_putd(ctx)
        return "bvoid"
    if function_name == "shift":
        assert len(params_data) == 2
        ptr_expression, ident_value = params_data
        ptr_type = parse_expr(ctx, ptr_expression)
        ident_type = parse_expr(ctx, ident_value)
        assert is_pointer(ptr_type) and ident_type == "bint"
        shift(ctx, ptr_type[:-1])
        return ptr_type
    if function_name == "deref":
        assert len(params_data) == 1
        expr_type = parse_expr(ctx, params_data[0])
        assert is_pointer(expr_type)
        deref_ptr_and_push(ctx)
        return expr_type[:-1]
    if function_name == "addr":
        assert len(params_data) == 1
        tag, data = params_data[0]
        assert tag == VAR, (tag, data)
        ctx.parameters.append(f"%{data}")
        return ctx.variables[data] + "*"
    if function_name == "as_p":
        assert len(params_data) == 2
        ptr_expression, assign_value = params_data
        ptr_type = parse_expr(ctx, ptr_expression)
        assign_type = parse_expr(ctx, assign_value)
        assert is_pointer(ptr_type) and assign_type == ptr_type[:-1], (ptr_type, assign_type)
        assign_ptr(ctx, ptr_type[:-1])
        return LLVM.void
    if function_name == "array_from_lit":
        assert len(params_data) == 1 and params_data[0][0] == LITERAL, params_data
        params_data = params_data[0][1][1:-1]
        create_array_and_push(ctx, LLVM.byte, len(params_data) + 1)  # ptr ptr + 1
        llvm_duplicate(ctx)
        for param in params_data:
            llvm_duplicate(ctx)
            llvm_push_number(ctx, ord(param))
            assign_ptr(ctx, LLVM.byte)
            llvm_push_number(ctx, 1)
            shift(ctx, LLVM.byte)
        llvm_push_number(ctx, 0)
        assign_ptr(ctx, LLVM.byte)
        return LLVM.ptr_byte
    if function_name == "array_from":
        create_array_and_push(ctx, LLVM.int, len(params_data))  # ptr ptr + 1
        llvm_duplicate(ctx)
        for param in params_data:
            tag, data = param
            if tag == "unary_minus":
                tag = NUMBER
                data = "-" + data[1]
            assert tag == NUMBER, param
            llvm_duplicate(ctx)
            llvm_push_number(ctx, data)
            assign_ptr(ctx, LLVM.int)
            llvm_push_number(ctx, 1)
            shift(ctx, LLVM.int)
        llvm_pop(ctx)
        return LLVM.ptr_int
    if function_name == "array":
        assert len(params_data) == 2
        array_type_data, size = params_data
        assert array_type_data[0] == GENERIC_TYPE, array_type_data
        assert size[0] == "number"
        create_array_and_push(ctx, array_type_data[1], size[1])
        return array_type_data[1] + "*"
    assert 0, f"unknown system function {function_name}"
