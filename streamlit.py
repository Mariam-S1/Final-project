# frontend.py
import streamlit as st
from router import route_message  # Router function to handle input

st.set_page_config(page_title="ERP Chatbot", layout="wide")
st.title("ERP Assistant Chatbot 🤖")
st.markdown("Ask questions about sales, finance, inventory, analytics, or CRM!")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat history
for msg in st.session_state.chat_history:
    role = msg["role"]
    content = msg["content"]
    if role == "user":
        st.chat_message("user").write(content)
    else:
        st.chat_message("assistant").write(content)

# User input box
if user_input := st.chat_input("Type your message here..."):
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = route_message(user_input, st.session_state.chat_history)
            st.write(response)
    st.session_state.chat_history.append({"role": "assistant", "content": response})
