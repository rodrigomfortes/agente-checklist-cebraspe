import os
from typing import List, Literal, Union
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import Union
from pydantic import BaseModel



load_dotenv()


class MarcarConferido(BaseModel):
    """Ação para quando o usuário confirma que verificou um ou mais itens."""
    action: Literal["marcar_conferido"] = "marcar_conferido"
    itens: List[str] = Field(..., description="Uma lista de nomes de itens que o usuário confirmou. Ex: ['canetas', 'alicate']")

class VerificarFaltantes(BaseModel):
    """Ação para quando o usuário pergunta o que ainda falta na checklist."""
    action: Literal["verificar_faltantes"] = "verificar_faltantes"

class ResetarChecklist(BaseModel):
    """Ação para quando o usuário pede para reiniciar ou limpar a conferência."""
    action: Literal["resetar_checklist"] = "resetar_checklist"

class IniciarDia(BaseModel):
    """Ação para iniciar um novo dia de checklist (ex: Dia 2)."""
    action: Literal["iniciar_dia"] = "iniciar_dia"
    dia: int = Field(..., description="Número do dia que o usuário deseja iniciar. Ex: 2")



PossibleActions = Union[MarcarConferido, VerificarFaltantes, ResetarChecklist, IniciarDia]

# --- Lógica do LangChain ---

def criar_parser_langchain():
    """
    Configura o LLM da OpenAI para usar nossas ações Pydantic como ferramentas.
    """
    from langchain_core.output_parsers.openai_tools import PydanticToolsParser

    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    structured_llm = (
        llm.bind_tools([MarcarConferido, VerificarFaltantes, ResetarChecklist,IniciarDia])
        | PydanticToolsParser(tools=[MarcarConferido, VerificarFaltantes, ResetarChecklist, IniciarDia])
    )

    return structured_llm

def parse_mensagem_usuario(texto: str) -> BaseModel:
    """
    A função principal que você vai entregar.
    Recebe o texto do usuário e retorna um objeto Pydantic com a ação e os dados.
    """

    prompt = f"""
    Analise a seguinte mensagem de um usuário que está conferindo uma checklist de materiais.
    Sua tarefa é identificar a intenção do usuário e extrair os nomes dos itens mencionados,
    formatando sua resposta de acordo com uma das ações disponíveis.
    
    Seja preciso na extração dos nomes dos itens.
    
    Mensagem do usuário: "{texto}"
    """
    
    resultado_acao = criar_parser_langchain().invoke(prompt)

    
    return resultado_acao


if __name__ == '__main__':
    print("Parser LangChain pronto para testes.")
    
    mensagem1 = "Opa, já conferi aqui os crachás, a fita adesiva e também o alicate."
    acao_detectada1 = parse_mensagem_usuario(mensagem1)
    
    print(f"\n[Teste 1] Mensagem: '{mensagem1}'")
    print("Tipo de Objeto Python:", type(acao_detectada1))
    # .model_dump() converte o objeto Pydantic para um dicionário Python
    print("Dicionário Python:", acao_detectada1.model_dump())
    # .model_dump_json() converte diretamente para uma string JSON formatada
    print("Saída JSON (o que você entrega):", acao_detectada1.model_dump_json(indent=2))
    
    # --- Cenário 2: Usuário pergunta o que falta ---
    mensagem2 = "Beleza. O que eu ainda preciso checar?"
    acao_detectada2 = parse_mensagem_usuario(mensagem2)
    
    print(f"\n[Teste 2] Mensagem: '{mensagem2}'")
    print("Saída JSON:", acao_detectada2.model_dump_json(indent=2))

    # --- Cenário 3: Usuário pede para reiniciar ---
    mensagem3 = "vamos começar do zero, reseta a lista por favor"
    acao_detectada3 = parse_mensagem_usuario(mensagem3)
    
    print(f"\n[Teste 3] Mensagem: '{mensagem3}'")
    print("Saída JSON:", acao_detectada3.model_dump_json(indent=2))

