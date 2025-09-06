"""
nl2sql_agent.py
---------------
Convert natural language questions into safe SQL queries using Gemini + RAG.
"""

import re
from langchain_google_genai import ChatGoogleGenerativeAI
from rag import load_vectorstore

class NL2SQLAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0)
        self.retriever = load_vectorstore().as_retriever(search_kwargs={"k": 4})

    def build_prompt(self, question: str) -> str:
        docs = self.retriever.get_relevant_documents(question)
        context = "\n\n".join([d.page_content for d in docs])
        return f"""
You are a SQL expert for an ERP database.
Use the schema and rules below to write a single SAFE SQL SELECT query.

Context:
{context}

Rules:
- SELECT only. Never DROP, DELETE, UPDATE, INSERT, ALTER, CREATE, PRAGMA.
- Return ONLY the SQL.

User question: {question}
SQL:
"""

    def generate_sql(self, question: str) -> str:
        prompt = self.build_prompt(question)
        response = self.llm.predict(prompt).strip()
        match = re.search(r"(SELECT[\s\S]*)", response, re.IGNORECASE)
        sql = match.group(1).strip() if match else response

        forbidden = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "PRAGMA"]
        if any(f in sql.upper() for f in forbidden):
            raise ValueError(f"⚠️ Unsafe SQL detected: {sql}")
        return sql
