import os
from typing import List, Literal, TypedDict, Union
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END


from database import ChecklistDatabase, init_database

# --- 1. Definição do Estado do Grafo ---
class GraphState(TypedDict):
    """
    Representa o estado do nosso sistema. Agora inclui um ID de sessão.
    """
    sessao_id: str
    original_input: str
    parsed_action: dict
    execution_result: Union[str, list] 
    final_response: str


# --- AGENTE 1: PARSER ---

class AtualizarItem(BaseModel):
    """Ação para marcar um item específico como presente."""
    action: Literal["atualizar_item"] = "atualizar_item"
    campo: str = Field(..., description="O nome exato do campo na base de dados a ser atualizado. Ex: 'lista_presenca_sala'")

class ListarFaltantes(BaseModel):
    """Ação para quando o utilizador pergunta o que ainda falta."""
    action: Literal["listar_faltantes"] = "listar_faltantes"

class ResetarChecklist(BaseModel):
    """Ação para quando o utilizador pede para reiniciar a checklist."""
    action: Literal["resetar_checklist"] = "resetar_checklist"

class IniciarChecklist(BaseModel):
    """Ação para criar uma nova checklist para o dia 1 ou 2."""
    action: Literal["iniciar_checklist"] = "iniciar_checklist"
    dia: int = Field(..., description="O número do dia para iniciar (1 ou 2).")

class AcaoNaoReconhecida(BaseModel):
    """Ação para quando a intenção do utilizador não é clara."""
    action: Literal["acao_nao_reconhecida"] = "acao_nao_reconhecida"

PossibleActions = Union[AtualizarItem, ListarFaltantes, ResetarChecklist, IniciarChecklist, AcaoNaoReconhecida]

class Router(BaseModel):
    action: PossibleActions = Field(..., discriminator="action")

llm_parser = ChatOpenAI(model="gpt-4o", temperature=0).with_structured_output(Router)

def parser_node(state: GraphState) -> GraphState:
    """O Agente Parser: interpreta a mensagem e mapeia para um campo da base de dados."""
    print("--- A entrar no Agente Parser ---")
    texto_usuario = state['original_input']
    
    campos_disponiveis = "lista_presenca, ata_sala, cartao_resposta, envelope_porta_objetos, folhas_rascunho, manuais, crachas, alicate, canetas, pinceis, fita_adesiva"
    
    prompt = f"""
    Você é um assistente de logística que mapeia pedidos de utilizadores para ações numa base de dados.
    A sua tarefa é analisar a mensagem e escolher a ação correta.
    Para a ação 'atualizar_item', você DEVE mapear o pedido para um dos seguintes campos: {campos_disponiveis}.

    Exemplos:
    - "conferi a ata de sala do primeiro dia" -> {{"action": "atualizar_item", "campo": "ata_sala"}}
    - "iniciar checklist do dia 1" -> {{"action": "iniciar_checklist", "dia": 1}}
    - "o que falta?" -> {{"action": "listar_faltantes"}}
    - "bom dia" -> {{"action": "acao_nao_reconhecida"}}

    Analise a mensagem do utilizador: "{texto_usuario}"
    """
    router_result = llm_parser.invoke(prompt)
    state['parsed_action'] = router_result['action']
    return state

# --- AGENTE 2: EXECUTOR ---
def executor_node(state: GraphState) -> GraphState:
    """O Agente Executor: chama os métodos reais da classe ChecklistDatabase."""
    print("--- A entrar no Agente Executor ---")
    action = state['parsed_action']
    sessao_id = state['sessao_id']
    
    db_manager = ChecklistDatabase()
    resultado = "Ação executada." 

    if action['action'] == "atualizar_item":
        try:
            db_manager.atualizar_item_dia1(sessao_id=sessao_id, campo=action['campo'], presente=True)
            resultado = f"Item '{action['campo']}' marcado como presente."
        except Exception as e:
            resultado = f"Erro ao atualizar o item: {e}"

    elif action['action'] == "listar_faltantes":
        resultado = db_manager.listar_faltantes(sessao_id=sessao_id) # Retorna uma lista
    
    elif action['action'] == "resetar_checklist":
        db_manager.resetar_checklist(sessao_id=sessao_id)
        resultado = "Checklist reiniciada com sucesso."

    elif action['action'] == "iniciar_checklist":
        dia = action.get('dia', 1)
        if dia == 1:
            db_manager.criar_checklist_dia1(sessao_id=sessao_id)
        else:
            db_manager.criar_checklist_dia2(sessao_id=sessao_id)
        resultado = f"Checklist para o Dia {dia} iniciada para a sessão {sessao_id}."
    
    else: 
        resultado = "Nenhuma ação de execução necessária."

    state['execution_result'] = resultado
    return state

# --- AGENTE 3: NOTIFICADOR  ---
def notifier_node(state: GraphState) -> GraphState:
    """O Agente Notificador: cria a resposta final para o utilizador."""
    print("--- A entrar no Agente Notificador ---")
    action_type = state['parsed_action']['action']
    resultado = state['execution_result']

    if action_type == "acao_nao_reconhecida":
        resposta_final = "Desculpe, não entendi o seu pedido. Pode tentar novamente?"
    elif action_type == "listar_faltantes":
        if isinstance(resultado, list) and resultado:
            itens_str = "\n- ".join(resultado)
            resposta_final = f"Itens que ainda faltam ser conferidos:\n- {itens_str}"
        elif isinstance(resultado, list) and not resultado:
            resposta_final = "✅ Parabéns! Todos os itens desta checklist já foram conferidos."
        else:
            resposta_final = f"Não foi possível listar os itens: {resultado}"
    else:
        resposta_final = f"✅ {resultado}"
    
    state['final_response'] = resposta_final
    return state

# --- 4. Construção e Compilação do Grafo ---
def create_multi_agent_app():
    load_dotenv()
    workflow = StateGraph(GraphState)

    workflow.add_node("parser_node", parser_node)
    workflow.add_node("executor_node", executor_node)
    workflow.add_node("notifier_node", notifier_node)

    workflow.set_entry_point("parser_node")
    workflow.add_conditional_edges(
        "parser_node",
        lambda state: "notifier_node" if state['parsed_action']['action'] == 'acao_nao_reconhecida' else "executor_node",
        {"executor_node": "executor_node", "notifier_node": "notifier_node"}
    )
    workflow.add_edge("executor_node", "notifier_node")
    workflow.add_edge("notifier_node", END)

    return workflow.compile()

multi_agent_app = create_multi_agent_app()

if __name__ == "__main__":
    print("🚀 A inicializar a base de dados...")
    init_database()
    
    TEST_SESSION_ID = "sessao_whatsapp_12345"
    print(f"Usando ID de sessão de teste: {TEST_SESSION_ID}")
    
    print("\n--- Teste 1: Iniciar Checklist ---")
    inputs1 = {"sessao_id": TEST_SESSION_ID, "original_input": "iniciar a checklist do dia 1"}
    result1 = multi_agent_app.invoke(inputs1)
    print("Resposta final:", result1['final_response'])
    
    print("\n--- Teste 2: Marcar Item ---")
    inputs2 = {"sessao_id": TEST_SESSION_ID, "original_input": "conferi os crachás"}
    result2 = multi_agent_app.invoke(inputs2)
    print("Resposta final:", result2['final_response'])

    print("\n--- Teste 3: Listar Faltantes ---")
    inputs3 = {"sessao_id": TEST_SESSION_ID, "original_input": "o que falta conferir?"}
    result3 = multi_agent_app.invoke(inputs3)
    print("Resposta final:", result3['final_response'])