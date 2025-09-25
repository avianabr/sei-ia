import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random
from python_sei.client import Client
from python_sei.models import Usuario, RetornoConsultaProcedimento, RetornoConsultaDocumento, Andamento
import zeep
from oci.addons.adk import Agent, AgentClient, tool
from typing import Dict, Any
from oci.addons.adk import Agent, AgentClient, tool
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.chat_models import ChatOCIGenAI
from langchain.chains.combine_documents.map_reduce import MapReduceDocumentsChain
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.combine_documents.reduce import ReduceDocumentsChain
from langchain_docling.loader import ExportType, DoclingLoader
from oci.addons.adk.tool.prebuilt import AgenticRagTool
import uvicorn
from python_sei.client import Client
from python_sei.models import Usuario, RetornoConsultaProcedimento, RetornoConsultaDocumento, Andamento
import zeep
import nest_asyncio


app = FastAPI()


id_unidade_teste = "110047993"
id_usuario_teste = "00029443830"

class Message(BaseModel):
    message: str
    session_id: str

@app.post("/session")
def create_session() -> Dict[str, Any]:
    session_id = agent.create_session("sei-ai-session")
    output = Message(message="session created" ,session_id=session_id),  
    return {"session_id": session_id, "message": "Session created successfully."}


@app.post("/chat")  
def chat(input: Message) -> Dict[str, Any]:
    
    response = agent.run(input=input.message, session_id=input.session_id)
    output = Message(message=response.final_output,session_id=response.session_id),  
    return {"message": response.final_output, "session_id": response.session_id}
    
@tool
def get_usuario(id_unidade: str, id_usuario:str) -> list[Usuario]:
    """
    retorna informacoes sobre o usuario lotado em uma unidade.

    Args:
    id_unidade(str): id da unidade do usuario
    id_usuario(str): id do usuario
    """

    usuarios = sei_client.listar_usuarios(id_unidade=id_unidade_teste, id_usuario=id_usuario_teste)

    return usuarios

@tool
def get_processo(id_unidade: str, protocolo_processo: str) -> Any:
    """
        retorna informacoes sobre um processo do SEI.

        Args:
            id_unidade(str): id da unidade do usuario
            protocolo_processo(str): numero do protocolo do processo.
    """
    

    procedimento = sei_client.consultar_procedimento(id_unidade_teste, protocolo_processo, True, True, True, True, True, True, True, True, True)
    return procedimento

@tool
def get_documento(id_unidade: str, protocolo_documento: str) -> Any:
    """
        retorno informacoes sobre um documento do SEI.

        Args:
        id_unidade: sigla da unidade do usuario
        protocolo_documento: numero do protocolo do documento.
    """
    
    documento = sei_client.consultar_documento(id_unidade_teste, protocolo_documento, True, True, False, True)
    return documento


@tool
def resumir_documento(id_unidade: str, protocolo_documento: str) -> Any:
    """
        resume o conteudo de um documento do sei.

        Args:
        sigla_unidade: sigla da unidade do usuario
        protocolo_documento: numero do protocolo do documento. 
    """
    documento = sei_client.consultar_documento(id_unidade_teste, protocolo_documento)
    
    # Load document from URL using docling
    loader = DoclingLoader(file_path=documento.link_acesso)
    docs = loader.load()

    
    # Initialize the Oracle Cloud Generative AI LLM
    llm = ChatOCIGenAI(
        model_id="meta.llama-3.3-70b-instruct",
        service_endpoint="https://inference.generativeai.sa-saopaulo-1.oci.oraclecloud.com",
        #alterar para o compartment_id do ambiente desejado
        compartment_id="ocid1.compartment.oc1..aaaaaaaamrvydbfbzcb3ys7dln2sl2giax43iuf6zi6uny3inhtu46ummv7a",
        model_kwargs={"temperature": 0},
    )

    # This controls how each document will be formatted. Specifically,
    # it will be passed to `format_document` - see that function for more
    # details.
    document_prompt = PromptTemplate(
        input_variables=["page_content"],
        template="{page_content}"
    )

    document_variable_name = "context"
    prompt = PromptTemplate.from_template(
        "crie um breve resumo do seguinte documento: {context}"
    )
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    # We now define how to combine these summaries
    reduce_prompt = PromptTemplate.from_template(
    "combine esses resumos: {context}"
    )
    reduce_llm_chain = LLMChain(llm=llm, prompt=reduce_prompt)
    combine_documents_chain = StuffDocumentsChain(
    llm_chain=reduce_llm_chain,
    document_prompt=document_prompt,
    document_variable_name=document_variable_name
    )
    reduce_documents_chain = ReduceDocumentsChain(
    combine_documents_chain=combine_documents_chain,
    )
    chain = MapReduceDocumentsChain(
    llm_chain=llm_chain,
    reduce_documents_chain=reduce_documents_chain,
    )
    # If we wanted to, we could also pass in collapse_documents_chain
    # which is specifically aimed at collapsing documents BEFORE
    # the final call.
    prompt = PromptTemplate.from_template(
    "junte esse conteudo em um resumo conciso, depois traduza para portugues do brasil: {context}"
    )
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    collapse_documents_chain = StuffDocumentsChain(
    llm_chain=llm_chain,
    document_prompt=document_prompt,
    document_variable_name=document_variable_name
    )
    reduce_documents_chain = ReduceDocumentsChain(
    combine_documents_chain=combine_documents_chain,
    collapse_documents_chain=collapse_documents_chain,
    )
    chain = MapReduceDocumentsChain(
    llm_chain=llm_chain,
    reduce_documents_chain=reduce_documents_chain,
    )

    # Run the chain
    summary = chain.invoke(docs)
    return summary.get("output_text")


@tool
def convert_documento(id_unidade: str, protocolo_documento: str) -> Any:
    """
        converte o conteudo de um documento do sei para texto plano.

        Args:
        id_unidade: id da unidade do usuario
        protocolo_documento: numero do protocolo do documento.
    """
    
    
    documento = sei_client.consultar_documento(id_unidade_teste, protocolo_documento)
    
    # Load document from URL using docling
    loader = DoclingLoader(file_path=documento.link_acesso)
    docs = loader.load()
    content = [doc.page_content for doc in docs]
    return {"content": content}


def executar_api():
    """
    Executa a API do agente SEI.
    """
  
    uvicorn.run(app, host="0.0.0.0", port=8000)

def main():
    """ Main function to run the SeiAgentClient API.
    """
    nest_asyncio.apply()

    global sei_client, agent_client, agent
          
    sei_client = Client(
        #alterar para o ambiente desejado
        url="https://homologacaoia.sei.sp.gov.br/sei/controlador_ws.php?servico=sei",
        sigla_sistema="ORACLE",
        identificacao_servico="8d1db23b8a93f414580c54db9699a67e202816abc14ee782470ea01728d09aba52b34ee9"
    )

    agent_client = AgentClient(
        auth_type="api_key",
        profile="DEFAULT",
        region="sa-saopaulo-1",
        debug=True,
    )

    agent = Agent(
        client=agent_client,
        display_name="sei-ai",
        #alterar para o compartment_id do ambiente desejado
        compartment_id="ocid1.compartment.oc1..aaaaaaaamrvydbfbzcb3ys7dln2sl2giax43iuf6zi6uny3inhtu46ummv7a",
        #alterar para o agent_endpoint_id do ambiente desejado
        agent_endpoint_id="ocid1.genaiagentendpoint.oc1.sa-saopaulo-1.amaaaaaa6g6dsrya5v5x2tonqcww7kfhr6xfqousu7tiib4lzievvypdhm2q",
        description="Um agente para interagir com o sistema SEI.",
        instructions="O id do usuario  e '00029443830'. o id da unidade e 110047993. Use as ferramentas disponíveis para obter informações sobre processos e documentos no sistema SEI. Use a ferramenta rag para pesquisar semanticamente os documentos. Para obter informações sobre um processo, utilize a ferramenta get_processo. Para obter informações sobre um documento, utilize a ferramenta get_documento. Para resumir o conteúdo de um documento, utilize a ferramenta resumir_documento. Para converter o conteúdo de um documento para texto plano, utilize a ferramenta convert_documento. Sempre que possível, forneça respostas detalhadas e completas.",

        tools=[get_processo, get_documento, resumir_documento, convert_documento],
    )

    # Setup the agent
    agent.setup()

    executar_api()
    

if __name__ == "__main__":
    main()
