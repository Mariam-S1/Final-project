"""
frontend.py
-----------
Streamlit dashboard for querying ERP analytics.
"""

import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000/ask"

st.title("ERP Analytics Dashboard")
query = st.text_input("Ask a question:")

if st.button("Submit") and query:
    resp = requests.get(API_URL, params={"q": query}).json()
    st.subheader("Generated SQL")
    st.code(resp["sql"])
    st.subheader("Results")
    df = pd.DataFrame(resp["results"])
    st.dataframe(df)
