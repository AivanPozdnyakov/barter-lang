def transform_params(params) -> list[Param]:
    if len(params):
        params = [tuple(param[1]) for param in params[1]]
    else:
        params = []
    return [(typeof, name) for typeof, name in params]


def parse_function_header(ctx: Context, function_name: str, params, return_type: BarterType):
    params = transform_params(params)
    params_types = [typeof for typeof, _ in params]
    ctx.signatures[function_name] = FunctionSignature(params_types, return_type)
    params_as_str = ",".join([str(param_type) for param_type in params_types])
    ctx.listing.append(f"define {return_type} @{function_name}({params_as_str}){{")
    assert len(set([name for _, name in params])) == len(params)
    for i, param in enumerate(params):
        typeof, name = param
        llvm_declare(ctx, name, typeof)
        ctx.variables[name] = typeof
        ctx.parameters.append(f"%{i}")
        llvm_assign(ctx, name, typeof)
    add_register(ctx, len(params))


def parse_function(ctx: Context, data):
    function_name, params, return_type = data[:3]
    function_body = data[3:]
    parse_function_header(ctx, function_name, params, return_type)
    ctx.current_return_type = return_type
    if return_type != "bvoid":
        llvm_declare(ctx, "return", return_type)
    parse_block(ctx, function_body)
    llvm_end_function(ctx)
