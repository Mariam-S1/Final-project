"""
analytics_agent.py
------------------
Analytics Agent: Combines RAG retrieval, NL-to-SQL, and custom analytics tools.
"""

from typing import Any, Dict, Optional, List
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from rag import load_vectorstore
from nl2sql_agent import NL2SQLAgent
from db import SQLiteClient

# ======================================================
# Database client
# ======================================================
db = SQLiteClient("data/erp.db")
retriever = load_vectorstore().as_retriever(search_kwargs={"k": 4})
nl2sql = NL2SQLAgent()

# ======================================================
# Tools
# ======================================================
@tool
def get_schema_context(query: str) -> str:
    """Retrieve relevant schema and business rule context from the vector store."""
    docs = retriever.get_relevant_documents(query)
    return "\n\n".join([d.page_content for d in docs])

@tool
def run_dynamic_sql(question: str) -> str:
    """Generate and execute SQL dynamically based on a natural language question."""
    sql = nl2sql.generate_sql(question)
    results = db.run_query(sql)
    return f"SQL: {sql}\nResults: {results}"

@tool
def top_customers(_: str) -> str:
    """Get top 5 customers by total order value."""
    rows = db.run_query("""
        SELECT c.name, COUNT(o.id) AS orders, SUM(o.total) AS total_value
        FROM customers c
        JOIN orders o ON c.id = o.customer_id
        GROUP BY c.name
        ORDER BY total_value DESC
        LIMIT 5
    """)
    return str(rows)

@tool
def sales_trends(_: str) -> str:
    """Get monthly sales trend (last 6 months)."""
    rows = db.run_query("""
        SELECT strftime('%Y-%m', created_at) AS month,
               COUNT(*) AS order_count,
               SUM(total) AS total_sales
        FROM orders
        WHERE created_at >= date('now', '-6 months')
        GROUP BY month
        ORDER BY month DESC
    """)
    return str(rows)

# ======================================================
# Tools list
# ======================================================
ANALYTICS_TOOLS = [
    get_schema_context,
    run_dynamic_sql,
    top_customers,
    sales_trends,
]

# ======================================================
# Prompt
# ======================================================
ANALYTICS_SYSTEM = """You are an Analytics Agent specialized in ERP data, business intelligence, and SQL.
Your responsibilities:
- Use schema context (via get_schema_context) to guide your reasoning
- Safely generate SQL with run_dynamic_sql
- Provide clear summaries and actionable insights
- Never use destructive queries
"""

ANALYTICS_PROMPT = PromptTemplate.from_template("""
{ANALYTICS_SYSTEM}

Available Tools:
{tool_names}

User Query: {input}
Chat History: {chat_history}
""")

# ======================================================
# Agent Setup
# ======================================================
llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0)
analytics_agent = create_react_agent(
    llm=llm,
    tools=ANALYTICS_TOOLS,
    prompt=ANALYTICS_PROMPT,
)

analytics_agent_executor = AgentExecutor(
    agent=analytics_agent,
    tools=ANALYTICS_TOOLS,
    verbose=True,
    max_iterations=10,
    handle_parsing_errors=True,
)

def run_analytics_agent(
    query: str, chat_history: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Run the analytics agent with a query."""
    return analytics_agent_executor.invoke({
        "input": query,
        "chat_history": chat_history or [],
    })
