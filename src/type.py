# type is just a string
# besides, it's different from llvm, so it would be bint and so on
# but whenever it need to be translated to llvm type, we assure that the type is correct
from src.data_structure import Context, LLVM_Type, BarterType

barter_to_llvm = {"bvoid": "void", "bint": "i32", "bfloat": "float", "bbool": "i8"}


def is_llvm_type(ctx: Context, s: str) -> bool:
    return s in list(barter_to_llvm.values()) or s in ctx.structs


def is_void(typeof: LLVM_Type) -> bool:
    return typeof == "bvoid"


def to_llvm_type(ctx: Context, barter_type: BarterType) -> LLVM_Type:
    assert barter_type in barter_to_llvm or barter_type in ctx.structs
    without_stars = barter_type.rstrip("*")
    stars = "*" * (len(barter_type) - len(without_stars))
    return barter_to_llvm.get(without_stars, without_stars) + stars


def to_ptr(ctx: Context, barter_type: BarterType) -> BarterType:
    assert barter_type in barter_to_llvm or barter_type in ctx.structs
    assert barter_type != "bvoid"
    return barter_type + "*"
