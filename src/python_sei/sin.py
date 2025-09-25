from typing import Literal


def decode_sin(value: str | None) -> bool | None:
    """Transforma uma string com valores S/N em bool"""
    if value is None:
        return None

    match value.lower():
        case "n":
            return False
        case "s":
            return True
        case _:
            raise ValueError("Invalid SIN")


def encode_sin(value: bool | None) -> Literal["S", "N"] | None:
    """Transforma um valor bool em S/N"""
    if value is None:
        return None
    return "S" if value else "N"
