# agents/analytics_agent.py
import json
from typing import Dict, Any, List
from langchain.tools import tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from db import SQLiteClient
from rag import get_retriever

# =========================================================
# SETUP: DB + LLM + RETRIEVER
# =========================================================
db_client = SQLiteClient(db_path="data/erp")  # Adjust path if needed
llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0)
retriever = get_retriever()

# =========================================================
# TOOL 1: TEXT-TO-SQL
# =========================================================
@tool
def text_to_sql_tool(question: str) -> str:
    """
    Converts a natural language analytics question into SQL and executes it.
    """
    try:
        # Ask LLM to write SQL (simplified, could use NL2SQLAgent)
        sql_prompt = f"Write a SQLite query for this question:\n{question}\nOnly give SQL."
        sql_query = llm.invoke(sql_prompt).content.strip()

        # Execute query
        result = db_client.run_query(sql_query)
        return json.dumps({"sql": sql_query, "result": result}, indent=2)
    except Exception as e:
        return f"Error generating or running SQL: {str(e)}"

# =========================================================
# TOOL 2: RAG DEFINITIONS
# =========================================================
@tool
def rag_definition_tool(term: str) -> str:
    """
    Retrieve glossary definitions or explanations of metrics and business rules.
    """
    try:
        docs = retriever.get_relevant_documents(term)
        return "\n\n".join([d.page_content for d in docs])
    except Exception as e:
        return f"Error retrieving definition: {str(e)}"

# =========================================================
# TOOL 3: KPI DASHBOARD ANALYTICS
# =========================================================
@tool
def analytics_tool(_: str = "") -> str:
    """
    Provides key business KPIs like sales, revenue, and stock levels.
    """
    try:
        queries = {
            "total_sales": "SELECT SUM(total) as total_sales FROM orders;",
            "top_customers": """
                SELECT c.name, SUM(o.total) as total_value
                FROM customers c
                JOIN orders o ON c.id = o.customer_id
                GROUP BY c.id
                ORDER BY total_value DESC
                LIMIT 5;
            """,
            "low_stock": """
                SELECT p.name, s.qty_on_hand
                FROM stock s
                JOIN products p ON s.product_id = p.id
                WHERE s.qty_on_hand <= s.reorder_point
                LIMIT 5;
            """
        }
        results = {k: db_client.run_query(q) for k, q in queries.items()}
        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error running analytics: {str(e)}"

# =========================================================
# AGENT SETUP
# =========================================================
ANALYTICS_SYSTEM = """
You are the ERP Analytics Agent. You can:
1. Convert natural language to SQL and run it.
2. Retrieve metric definitions and docs via RAG.
3. Provide dashboards with key performance indicators.
"""

ANALYTICS_PROMPT = PromptTemplate.from_template("""
{ANALYTICS_SYSTEM}

Available Tools:
{text_to_sql_tool}, {rag_definition_tool}, {analytics_tool}

User Query: {input}
Chat History: {chat_history}
""")

analytics_agent = create_react_agent(
    llm=llm,
    tools=[text_to_sql_tool, rag_definition_tool, analytics_tool],
    prompt=ANALYTICS_PROMPT,
)

analytics_agent_executor = AgentExecutor(
    agent=analytics_agent,
    tools=[text_to_sql_tool, rag_definition_tool, analytics_tool],
    verbose=True,
    handle_parsing_errors=True,
)

def run_analytics_agent(query: str, chat_history: List[Dict[str, Any]] = None) -> Any:
    """
    Main entry point: pass in a query, get agent response.
    """
    return analytics_agent_executor.invoke({
        "input": query,
        "chat_history": chat_history or [],
    })
