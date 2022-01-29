from dataclasses import dataclass, field


@dataclass
class FunctionSignature:
    number_of_parameters: int


@dataclass
class Context:
    variables: set[str] = field(default_factory=set)
    listing: list[str] = field(default_factory=list)
    parameters: list[str] = field(default_factory=list)
    signatures: dict[str, FunctionSignature] = field(default_factory=dict)
    register_counter = 0
    branch_temp_indexes: list[int] = field(default_factory=list)
    loop_temp_indexes: list[int] = field(default_factory=list)
    loop_labels: list[str] = field(default_factory=list)
