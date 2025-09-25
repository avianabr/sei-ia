from enum import Enum


class Aplicabilidade(Enum):
    DOCUMENTOS_INTERNOS_EXTERNOS = 0
    DOCUMENTOS_INTERNOS = 1
    DOCUMENTOS_EXTERNOS = 2
    FORMULARIOS = 3

    @staticmethod
    def from_str(value: str):
        match value:
            case "T":
                return Aplicabilidade.DOCUMENTOS_INTERNOS_EXTERNOS
            case "I":
                return Aplicabilidade.DOCUMENTOS_INTERNOS
            case "E":
                return Aplicabilidade.DOCUMENTOS_EXTERNOS
            case "F":
                return Aplicabilidade.FORMULARIOS
            case _:
                raise ValueError("Invalid Aplicabilidade value")

    def to_str(self) -> str:
        match self:
            case Aplicabilidade.DOCUMENTOS_INTERNOS_EXTERNOS:
                return "T"
            case Aplicabilidade.DOCUMENTOS_INTERNOS:
                return "I"
            case Aplicabilidade.DOCUMENTOS_EXTERNOS:
                return "E"
            case Aplicabilidade.FORMULARIOS:
                return "F"
            case _:
                raise ValueError("Invalid Aplicabilidade value")


class NivelAcesso(Enum):
    PUBLICO = 0
    RESTRITO = 1
    SIGILOSO = 2

    @staticmethod
    def from_str(value: str):
        match value:
            case "0":
                return NivelAcesso.PUBLICO
            case "1":
                return NivelAcesso.RESTRITO
            case "2":
                return NivelAcesso.SIGILOSO
            case _:
                raise ValueError("Invalid NivelAcesso value")

    def to_str(self) -> str:
        match self:
            case NivelAcesso.PUBLICO:
                return "0"
            case NivelAcesso.RESTRITO:
                return "1"
            case NivelAcesso.SIGILOSO:
                return "2"
            case _:
                raise ValueError("Invalid NivelAcesso")
