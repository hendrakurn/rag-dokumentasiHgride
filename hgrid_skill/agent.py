"""HGrid247 AI Agent - Orchestrator dengan tool calling."""
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent

from core.config import GEMINI_MODEL
from core.prompts import AGENT_SYSTEM_PROMPT
from hgrid_skill.tools.hgrid_api import search_docs, list_engines
from hgrid_skill.tools.script_runner import run_shell_command, run_hgrid_script
from hgrid_skill.tools.workflow_builder import create_workflow, list_workflow_components


def create_hgrid_agent():
    """Buat HGrid247 AI Agent dengan semua tools."""
    
    llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL)
    
    tools = [
        search_docs,
        list_engines,
        list_workflow_components,
        create_workflow,
        run_shell_command,
        run_hgrid_script,
    ]
    
    # Buat ReAct agent menggunakan LangGraph
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=AGENT_SYSTEM_PROMPT,
    )
    
    return agent


def run_agent(query: str, chat_history: list = None):
    """
    Jalankan agent dengan query user.
    
    Args:
        query: Permintaan user
        chat_history: Riwayat percakapan (opsional)
    
    Returns:
        dict: jawaban agent dan tools yang digunakan
    """
    agent = create_hgrid_agent()
    
    messages = []
    if chat_history:
        messages.extend(chat_history)
    messages.append(HumanMessage(content=query))
    
    result = agent.invoke({"messages": messages})
    
    # Ambil pesan terakhir (jawaban agent)
    final_message = result["messages"][-1]
    
    return {
        "jawaban": final_message.content,
        "tools_used": [
            msg.name for msg in result["messages"]
            if hasattr(msg, "name") and msg.name
        ],
    }
