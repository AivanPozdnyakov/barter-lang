from dataclasses import dataclass, field
from typing import Literal


class LlvmClass:
    type = Literal['i32', 'i8', 'f32', 'void']

    @property
    def int(self) -> str:
        return "i32"

    @property
    def float(self):
        return "f32"

    @property
    def bool(self):
        return "i8"

    @property
    def void(self):
        return "void"


LLVM = LlvmClass()


@dataclass
class FunctionSignature:
    parameters: list[LLVM.type]
    return_type: LLVM.type


@dataclass
class Context:
    return_index: list[int] = field(default_factory=list)
    return_value: str = None
    current_return_type: LLVM.type = None
    variables: dict[str, LLVM.type] = field(default_factory=dict)
    listing: list[str] = field(default_factory=list)
    parameters: list[str] = field(default_factory=list)
    signatures: dict[str, FunctionSignature] = field(default_factory=dict)
    register_counter = 0
    branch_temp_indexes: list[int] = field(default_factory=list)
    loop_temp_indexes: list[int] = field(default_factory=list)
    loop_labels: list[str] = field(default_factory=list)

    def clear(self):
        self.variables.clear()
        self.return_value = None
        self.current_return_type = None
        self.register_counter = 0
        assert len(self.parameters) == 0, self.parameters
        assert len(self.branch_temp_indexes) == 0
        assert len(self.loop_temp_indexes) == 0
        assert len(self.loop_labels) == 0
