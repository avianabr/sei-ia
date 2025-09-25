import zeep
import zeep.xsd
from zeep.helpers import serialize_object

from .models import (
    Andamento,
    DefinicaoControlePrazo,
    Marcador,
    RetornoConsultaDocumento,
    RetornoConsultaProcedimento,
    Serie,
    Unidade,
    Usuario,
)
from .sin import encode_sin


class Client:
    """
    TODO: Verificar os valores das constantes tarefas e taferas internas listadas
    no arquivo `TarefaRN.php`.
    """

    def __init__(self, url: str, sigla_sistema: str, identificacao_servico: str):
        self.sigla_sistema = sigla_sistema
        self.identificacao_servico = identificacao_servico
        self.client = zeep.Client(url)

    @property
    def _service(self):
        return self.client.service

    def listar_unidades(
        self,
        id_tipo_procedimento: str = "",
        id_serie: str = "",
    ) -> list[Unidade]:
        """Retorna a lista de unidades cadastradas no SEI"""
        records = self._service.listarUnidades(
            SiglaSistema=self.sigla_sistema,
            IdentificacaoServico=self.identificacao_servico,
            IdTipoProcedimento=id_tipo_procedimento,
            IdSerie=id_serie,
        )
        return Unidade.from_many_records(serialize_object(records))

    def listar_usuarios(
        self,
        id_unidade: str,
        id_usuario: str = "",
    ) -> list[Usuario]:
        """Retorna a lista de usuários de uma unidade"""
        records = self._service.listarUsuarios(
            SiglaSistema=self.sigla_sistema,
            IdentificacaoServico=self.identificacao_servico,
            IdUnidade=id_unidade,
            IdUsuario=id_usuario,
        )
        return Usuario.from_many_records(serialize_object(records))

    def consultar_procedimento(
        self,
        id_unidade: str,
        protocolo_procedimento: str,
        retornar_assuntos: bool = False,
        retornar_interessados: bool = False,
        retornar_observacoes: bool = False,
        retornar_andamento_geracao: bool = False,
        retornar_andamento_conclusao: bool = False,
        retornar_ultimo_andamento: bool = False,
        retornar_unidades_procedimento_aberto: bool = False,
        retornar_procedimentos_relacionados: bool = False,
        retornar_procedimentos_anexados: bool = False,
    ) -> RetornoConsultaProcedimento:
        record = self._service.consultarProcedimento(
            SiglaSistema=self.sigla_sistema,
            IdentificacaoServico=self.identificacao_servico,
            IdUnidade=id_unidade,
            ProtocoloProcedimento=protocolo_procedimento,
            SinRetornarAssuntos=encode_sin(retornar_assuntos),
            SinRetornarInteressados=encode_sin(retornar_interessados),
            SinRetornarObservacoes=encode_sin(retornar_observacoes),
            SinRetornarAndamentoGeracao=encode_sin(retornar_andamento_geracao),
            SinRetornarAndamentoConclusao=encode_sin(retornar_andamento_conclusao),
            SinRetornarUltimoAndamento=encode_sin(retornar_ultimo_andamento),
            SinRetornarUnidadesProcedimentoAberto=encode_sin(
                retornar_unidades_procedimento_aberto
            ),
            SinRetornarProcedimentosRelacionados=encode_sin(
                retornar_procedimentos_relacionados
            ),
            SinRetornarProcedimentosAnexados=encode_sin(
                retornar_procedimentos_anexados
            ),
        )
        return RetornoConsultaProcedimento.from_record(serialize_object(record))

    def definir_controle_prazo(
        self,
        id_unidade: str,
        definicoes: list[DefinicaoControlePrazo],
    ) -> None:
        self._service.definirControlePrazo(
            SiglaSistema=self.sigla_sistema,
            IdentificacaoServico=self.identificacao_servico,
            IdUnidade=id_unidade,
            Definicoes=[definicao.to_record() for definicao in definicoes],
        )

    def listar_marcadores_unidade(self, id_unidade: str) -> list[Marcador]:
        """Lista todos os marcadores de uma unidade."""
        records = self._service.listarMarcadoresUnidade(
            SiglaSistema=self.sigla_sistema,
            IdentificacaoServico=self.identificacao_servico,
            IdUnidade=id_unidade,
        )
        return Marcador.from_many_records(serialize_object(records))

    def listar_series(
        self,
        id_unidade: str = "",
        id_tipo_procedimento: str = "",
    ) -> list[Serie]:
        """
        Lista todas as séries, que são tipos de documentos como `Memorando`, `Despacho`, etc,
        disponíveis no SEI
        """
        records = self._service.listarSeries(
            SiglaSistema=self.sigla_sistema,
            IdentificacaoServico=self.identificacao_servico,
            IdUnidade=id_unidade,
            IdTipoProcedimento=id_tipo_procedimento,
        )
        return Serie.from_many_records(serialize_object(records))

    def consultar_documento(
        self,
        id_unidade: str,
        protocolo_documento: str,
        retornar_andamento_geracao: bool = False,
        retornar_assinaturas: bool = False,
        retornar_publicacao: bool = False,
        retornar_campos: bool = False,
    ):
        record = self._service.consultarDocumento(
            SiglaSistema=self.sigla_sistema,
            IdentificacaoServico=self.identificacao_servico,
            IdUnidade=id_unidade,
            ProtocoloDocumento=protocolo_documento,
            SinRetornarAndamentoGeracao=encode_sin(retornar_andamento_geracao),
            SinRetornarAssinaturas=encode_sin(retornar_assinaturas),
            SinRetornarPublicacao=encode_sin(retornar_publicacao),
            SinRetornarCampos=encode_sin(retornar_campos),
        )

        return RetornoConsultaDocumento.from_record(serialize_object(record))

    def listar_andamentos(
        self,
        id_unidade: str,
        protocolo_procedimento: str,
        retornar_atributos: bool = False,
        andamentos: list[str] = zeep.xsd.SkipValue,
        tarefas: list[str] = zeep.xsd.SkipValue,
        tarefas_modulos: list[str] = zeep.xsd.SkipValue,
    ):
        records = self._service.listarAndamentos(
            SiglaSistema=self.sigla_sistema,
            IdentificacaoServico=self.identificacao_servico,
            IdUnidade=id_unidade,
            ProtocoloProcedimento=protocolo_procedimento,
            SinRetornarAtributos=encode_sin(retornar_atributos),
            Andamentos=andamentos,
            Tarefas=tarefas,
            TarefasModulos=tarefas_modulos,
        )

        return Andamento.from_many_records(serialize_object(records))

    def listar_andamentos_marcadores(
        self,
        id_unidade: str,
        protocolo_procedimento: str,
        marcadores: list[str] = zeep.xsd.SkipValue,
    ):
        records = self._service.listarAndamentosMarcadores(
            SiglaSistema=self.sigla_sistema,
            IdentificacaoServico=self.identificacao_servico,
            IdUnidade=id_unidade,
            ProtocoloProcedimento=protocolo_procedimento,
            Marcadores=marcadores,
        )

        return records


