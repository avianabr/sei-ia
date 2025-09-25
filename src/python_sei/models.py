from dataclasses import dataclass
from typing import OrderedDict, Self

from .enums import Aplicabilidade, NivelAcesso
from .sin import decode_sin, encode_sin


class Model:
    _raw_value: OrderedDict | None = None

    @staticmethod
    def from_record(record: OrderedDict) -> Self: ...

    @classmethod
    def from_many_records(cls, records: list[dict]) -> list[Self]:
        return [cls.from_record(record) for record in records]

    @property
    def raw_value(self):
        return self._raw_value


@dataclass
class Assinatura(Model):
    nome: str
    cargo_funcao: str
    data_hora: str
    id_usuario: str
    id_origem: str
    id_orgao: str
    sigla: str

    @staticmethod
    def from_record(record):
        assinatura = Assinatura(
            nome=record["Nome"],
            cargo_funcao=record["CargoFuncao"],
            data_hora=record["DataHora"],
            id_usuario=record["IdUsuario"],
            id_origem=record["IdOrigem"],
            id_orgao=record["IdOrgao"],
            sigla=record["Sigla"],
        )

        assinatura._raw_value = record
        return assinatura


@dataclass
class Campo(Model):
    nome: str
    valor: str

    @staticmethod
    def from_record(record):
        campo = Campo(
            nome=record["Nome"],
            valor=record["Valor"],
        )

        campo._raw_value = record
        return campo


@dataclass
class Unidade(Model):
    id_unidade: str
    sigla: str
    descricao: str
    protocolo: bool | None
    arquivamento: bool | None
    ouvidoria: bool | None

    @staticmethod
    def from_record(record):
        unidade = Unidade(
            id_unidade=record["IdUnidade"],
            sigla=record["Sigla"],
            descricao=record["Descricao"],
            protocolo=decode_sin(record["SinProtocolo"]),
            arquivamento=decode_sin(record["SinArquivamento"]),
            ouvidoria=decode_sin(record["SinOuvidoria"]),
        )

        unidade._raw_value = record
        return unidade


@dataclass
class Usuario(Model):
    id_usuario: str
    sigla: str
    nome: str

    @staticmethod
    def from_record(record):
        usuario = Usuario(
            id_usuario=record["IdUsuario"],
            sigla=record["Sigla"],
            nome=record["Nome"],
        )
        usuario._raw_value = record
        return usuario


@dataclass
class AtributoAndamento(Model):
    nome: str
    valor: str
    id_origem: str

    @staticmethod
    def from_record(record):
        atributo = AtributoAndamento(
            nome=record["Nome"],
            valor=record["Valor"],
            id_origem=record["IdOrigem"],
        )

        atributo._raw_value = record
        return atributo


@dataclass
class Assunto(Model):
    codigo_estruturado: str | None
    descricao: str | None

    @staticmethod
    def from_record(record):
        assunto = Assunto(
            codigo_estruturado=record["CodigoEstruturado"],
            descricao=record["Descricao"],
        )

        assunto._raw_value = record
        return assunto


@dataclass
class ProcedimentoResumido(Model):
    id_tipo_procedimento: str
    procedimento_formatado: str
    tipo_procedimento: str

    @staticmethod
    def from_record(record):
        procedimento = ProcedimentoResumido(
            id_tipo_procedimento=record["IdTipoProcedimento"],
            procedimento_formatado=record["ProcedimentoFormatado"],
            tipo_procedimento=record["TipoProcedimento"],
        )

        procedimento._raw_value = record
        return procedimento


@dataclass
class Observacao(Model):
    descricao: str
    unidade: Unidade

    @staticmethod
    def from_record(record):
        observacao = Observacao(
            descricao=record["Descricao"],
            unidade=Unidade.from_record(record["Unidade"]),
        )

        observacao._raw_value = record
        return observacao


@dataclass
class Interessado(Model):
    sigla: str
    nome: str

    @staticmethod
    def from_record(record):
        interessado = Interessado(
            sigla=record["Sigla"],
            nome=record["Nome"],
        )

        interessado._raw_value = record
        return interessado


@dataclass
class Andamento(Model):
    id_andamento: str
    id_tarefa: str
    id_tarefa_modulo: str
    descricao: str
    data_hora: str
    unidade: Unidade | None
    usuario: Usuario | None
    atributos: list[AtributoAndamento] | None

    @staticmethod
    def from_record(record):
        if Andamento.is_blank(record):
            return None

        andamento = Andamento(
            id_andamento=record["IdAndamento"],
            id_tarefa=record["IdTarefa"],
            id_tarefa_modulo=record["IdTarefaModulo"],
            descricao=record["Descricao"],
            data_hora=record["DataHora"],
            unidade=None,
            usuario=None,
            atributos=None,
        )

        if record["Unidade"] is not None:
            andamento.unidade = Unidade.from_record(record["Unidade"])

        if record["Usuario"] is not None:
            andamento.usuario = Usuario.from_record(record["Usuario"])

        if record["Atributos"] is not None:
            andamento.atributos = AtributoAndamento.from_many_records(
                record["Atributos"]
            )

        andamento._raw_value = record
        return andamento

    @staticmethod
    def is_blank(record: OrderedDict) -> bool:
        return record == {
            "IdAndamento": None,
            "IdTarefa": None,
            "IdTarefaModulo": None,
            "Descricao": None,
            "DataHora": None,
            "Unidade": None,
            "Usuario": None,
            "Atributos": None,
        }


@dataclass
class Marcador(Model):
    id_marcador: str
    nome: str
    icone: str
    ativo: bool

    @staticmethod
    def from_record(record):
        marcador = Marcador(
            id_marcador=record["IdMarcador"],
            nome=record["Nome"],
            icone=record["Icone"],
            ativo=decode_sin(record["SinAtivo"]),
        )

        marcador._raw_value = record
        return marcador


@dataclass
class ArquivoExtensao(Model):
    id_andamento_marcador: str
    texto: str
    data_hora: str
    usuario: Usuario

    @staticmethod
    def from_record(record):
        extensao = ArquivoExtensao(
            id_andamento_marcador=record["IdAndamentoMarcador"],
            texto=record["Texto"],
            data_hora=record["DataHora"],
            usuario=Usuario.from_record(record["Usuario"]),
        )

        extensao._raw_value = record
        return extensao


@dataclass
class DefinicaoControlePrazo(Model):
    protocolo_procedimento: str
    data_prazo: str
    dias: str
    dias_uteis: bool

    def to_record(self) -> dict:
        return {
            "ProtocoloProcedimento": self.protocolo_procedimento,
            "DataPrazo": self.data_prazo,
            "Dias": self.dias,
            "SinDiasUteis": encode_sin(self.dias_uteis),
        }


@dataclass
class Serie(Model):
    id_serie: str
    nome: str
    aplicabilidade: Aplicabilidade | None

    @staticmethod
    def from_record(record):
        serie = Serie(
            id_serie=record["IdSerie"],
            nome=record["Nome"],
            aplicabilidade=None,
        )

        if record["Aplicabilidade"] is not None:
            serie.aplicabilidade = Aplicabilidade.from_str(record["Aplicabilidade"])

        serie._raw_value = record
        return serie


@dataclass
class TipoProcedimento(Model):
    id_tipo_procedimento: str
    nome: str

    @staticmethod
    def from_record(record):
        tipo_procedimento = TipoProcedimento(
            id_tipo_procedimento=record["IdTipoProcedimento"],
            nome=record["Nome"],
        )

        tipo_procedimento._raw_value = record
        return tipo_procedimento


@dataclass
class UnidadeProcedimentoAberto(Model):
    unidade: Unidade
    usuario_atribuido: Usuario

    @staticmethod
    def from_record(record):
        unidade = UnidadeProcedimentoAberto(
            unidade=Unidade.from_record(record["Unidade"]),
            usuario_atribuido=Usuario.from_record(record["UsuarioAtribuicao"]),
        )

        unidade._raw_value = record
        return unidade


@dataclass
class Publicacao(Model):
    id_publicacao: str
    id_documento: str
    sta_motivo: str
    resumo: str
    id_veiculo_publicacao: str
    nome_veiculo: str
    sta_tipo_veiculo: str
    numero: str
    data_disponibilizacao: str
    data_publicacao: str
    estado: str
    imprensa_nacional: str

    @staticmethod
    def from_record(record):
        if Publicacao.is_empty(record):
            return None

        return Publicacao(
            id_publicacao=record["IdPublicacao"],
            id_documento=record["IdDocumento"],
            sta_motivo=record["StaMotivo"],
            resumo=record["Resumo"],
            id_veiculo_publicacao=record["IdVeiculoPublicacao"],
            nome_veiculo=record["NomeVeiculo"],
            sta_tipo_veiculo=record["StaTipoVeiculo"],
            numero=record["Numero"],
            data_disponibilizacao=record["DataDisponibilizacao"],
            data_publicacao=record["DataPublicacao"],
            estado=record["Estado"],
            imprensa_nacional=record["ImprensaNacional"],
        )

    @staticmethod
    def is_empty(record: OrderedDict) -> bool:
        return record == {
            "IdPublicacao": None,
            "IdDocumento": None,
            "StaMotivo": None,
            "Resumo": None,
            "IdVeiculoPublicacao": None,
            "NomeVeiculo": None,
            "StaTipoVeiculo": None,
            "Numero": None,
            "DataDisponibilizacao": None,
            "DataPublicacao": None,
            "Estado": None,
            "ImprensaNacional": None,
        }


@dataclass
class RetornoConsultaProcedimento(Model):
    id_procedimento: str
    procedimento_formatado: str
    especificacao: str
    data_autuacao: str
    link_acesso: str
    nivel_acesso_local: NivelAcesso
    nivel_acesso_global: NivelAcesso
    tipo_procedimento: TipoProcedimento
    andamento_geracao: Andamento | None
    andamento_conclusao: Andamento | None
    ultimo_andamento: Andamento | None
    unidades_procedimento_aberto: list[UnidadeProcedimentoAberto]
    assuntos: list[Assunto]
    observacoes: list[Observacao]
    interessados: list[Interessado]
    procedimentos_relacionados: list[ProcedimentoResumido]
    procedimentos_anexados: list[ProcedimentoResumido]

    @staticmethod
    def from_record(record):
        procedimento = RetornoConsultaProcedimento(
            id_procedimento=record["IdProcedimento"],
            procedimento_formatado=record["ProcedimentoFormatado"],
            especificacao=record["Especificacao"],
            data_autuacao=record["DataAutuacao"],
            link_acesso=record["LinkAcesso"],
            nivel_acesso_local=NivelAcesso.from_str(record["NivelAcessoLocal"]),
            nivel_acesso_global=NivelAcesso.from_str(record["NivelAcessoGlobal"]),
            tipo_procedimento=TipoProcedimento.from_record(record["TipoProcedimento"]),
            andamento_geracao=Andamento.from_record(record["AndamentoGeracao"]),
            andamento_conclusao=Andamento.from_record(record["AndamentoConclusao"]),
            ultimo_andamento=Andamento.from_record(record["UltimoAndamento"]),
            unidades_procedimento_aberto=UnidadeProcedimentoAberto.from_many_records(
                record["UnidadesProcedimentoAberto"]
            ),
            assuntos=Assunto.from_many_records(record["Assuntos"]),
            observacoes=Observacao.from_many_records(record["Observacoes"]),
            interessados=Interessado.from_many_records(record["Interessados"]),
            procedimentos_relacionados=ProcedimentoResumido.from_many_records(
                record["ProcedimentosRelacionados"]
            ),
            procedimentos_anexados=ProcedimentoResumido.from_many_records(
                record["ProcedimentosAnexados"]
            ),
        )

        procedimento._raw_value = record
        return procedimento


@dataclass
class RetornoConsultaDocumento(Model):
    id_procedimento: str
    procedimento_formatado: str
    id_documento: str
    documento_formatado: str
    nivel_acesso_local: NivelAcesso
    nivel_acesso_global: NivelAcesso
    link_acesso: str
    serie: Serie
    numero: str | None
    nome_arvore: str | None
    descricao: str | None
    data: str
    unidade_elaboradora: Unidade
    andamento_geracao: Andamento | None
    assinaturas: list[Assinatura]
    publicacao: Publicacao | None
    campos: list[Campo]

    @staticmethod
    def from_record(record):
        documento = RetornoConsultaDocumento(
            id_procedimento=record["IdProcedimento"],
            procedimento_formatado=record["ProcedimentoFormatado"],
            id_documento=record["IdDocumento"],
            documento_formatado=record["DocumentoFormatado"],
            link_acesso=record["LinkAcesso"],
            nivel_acesso_local=NivelAcesso.from_str(record["NivelAcessoLocal"]),
            nivel_acesso_global=NivelAcesso.from_str(record["NivelAcessoGlobal"]),
            serie=Serie.from_record(record["Serie"]),
            numero=record["Numero"],
            nome_arvore=record["NomeArvore"],
            descricao=record["Descricao"],
            data=record["Data"],
            unidade_elaboradora=Unidade.from_record(record["UnidadeElaboradora"]),
            andamento_geracao=Andamento.from_record(record["AndamentoGeracao"]),
            assinaturas=Assinatura.from_many_records(record["Assinaturas"]),
            publicacao=Publicacao.from_record(record["Publicacao"]),
            campos=Campo.from_many_records(record["Campos"]),
        )

        documento._raw_value = record
        return documento
