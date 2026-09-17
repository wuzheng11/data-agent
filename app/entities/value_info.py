from dataclasses import dataclass

@dataclass
class ValueInfo:
    id: str # f"{column_id}.{value}"
    value: str
    column_id: str # f"{table.name}.{column.name}"
