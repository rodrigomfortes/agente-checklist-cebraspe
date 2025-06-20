import os
from typing import List, Literal, Union
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


load_dotenv()


class MarcarConferido(BaseModel):
    """Ação para quando o utilizador confirma que verificou um ou mais itens."""
    action: Literal["marcar_conferido"] = "marcar_conferido"
    itens: List[str] = Field(..., description="Uma lista de nomes de itens que o utilizador confirmou. Ex: ['canetas', 'alicate']")

class VerificarFaltantes(BaseModel):
    """Ação para quando o utilizador pergunta o que ainda falta na checklist."""
    action: Literal["verificar_faltantes"] = "verificar_faltantes"

class ResetarChecklist(BaseModel):
    """Ação para quando o utilizador pede para reiniciar ou limpar a conferência."""
    action: Literal["resetar_checklist"] = "resetar_checklist"
  
PossibleActions = Union[MarcarConferido, VerificarFaltantes, ResetarChecklist]


class Router(BaseModel):
    """Seleciona a melhor ação a ser tomada com base na consulta do utilizador."""
    action: PossibleActions = Field(..., discriminator="action")



llm_parser = ChatOpenAI(model="gpt-4o", temperature=0).with_structured_output(Router)


def parse_mensagem_usuario(texto: str) -> PossibleActions:
    """
    A função principal que o app.py irá importar e chamar.
    """
    prompt = f"""
    Analise a seguinte mensagem de um utilizador que está a conferir uma checklist de materiais.
    A sua tarefa é identificar a intenção do utilizador e extrair os nomes dos itens mencionados,
    formatando a sua resposta de acordo com uma das ações disponíveis.

    Seja preciso na extração dos nomes dos itens.

    Mensagem do utilizador: "{texto}"
    """
    

    router_result = llm_parser.invoke(prompt)
    

    return router_result.action



if __name__ == '__main__':
    print("🤖 Parser LangChain pronto para testes.")
    
    mensagem1 = "Opa, já conferi aqui os crachás, a fita adesiva e também o alicate."
    acao_detectada1 = parse_mensagem_usuario(mensagem1)
    
    print(f"\n[Teste 1] Mensagem: '{mensagem1}'")
    print("Saída JSON:", acao_detectada1.model_dump_json(indent=2))
    
    mensagem2 = "Beleza. O que eu ainda preciso de verificar?"
    acao_detectada2 = parse_mensagem_usuario(mensagem2)
    
    print(f"\n[Teste 2] Mensagem: '{mensagem2}'")
    print("Saída JSON:", acao_detectada2.model_dump_json(indent=2))

