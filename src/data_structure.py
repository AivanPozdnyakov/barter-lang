from dataclasses import dataclass, field

BarterType = str
LLVM_Type = str


@dataclass
class Param:
    type: BarterType
    name: str


@dataclass
class FunctionSignature:
    parameters: list[Param]
    return_type: BarterType


@dataclass
class SysSignature:
    parameters: list[str]
    return_type: BarterType


@dataclass
class StructType:
    parameters: list[BarterType]


@dataclass
class Context:
    listing: list[str] = field(default_factory=list)

    variables: dict[str, BarterType] = field(default_factory=dict)
    structs: dict[str, StructType] = field(default_factory=list)
    signatures: dict[str, FunctionSignature] = field(default_factory=dict)

    current_return_type: BarterType = None
    return_index: list[int] = field(default_factory=list)
    parameters: list[str] = field(default_factory=list)
    # sys_signatures: dict[str, SysSignature] = field(default_factory=dict)
    register_counter = 0

    branch_temp_indexes: list[int] = field(default_factory=list)
    loop_temp_indexes: list[int] = field(default_factory=list)
    loop_labels: list[str] = field(default_factory=list)

    def clear(self):
        self.variables.clear()
        self.current_return_type = None
        self.register_counter = 0
        assert len(self.parameters) == 0, self.parameters
        assert len(self.branch_temp_indexes) == 0
        assert len(self.loop_temp_indexes) == 0
        assert len(self.loop_labels) == 0
