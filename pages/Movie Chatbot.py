import streamlit as st
import requests
import google.generativeai as genai

OMDB_API_KEY = "89d15140"
GEMINI_API_KEY = "AIzaSyCQNy4vivWIVBlvT1hqRzz2VXs5nLuvPMU"

genai.configure(api_key=GEMINI_API_KEY)

st.title("🗣 Movie Chatbot")
st.markdown("Ask me anything about movies!")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "movie_context" not in st.session_state:
    st.session_state.movie_context = ""

def gen_resp(user_message):
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        pmt = f"""You are a helpful movie expert chatbot. You have access to the following movie information from OMDB:

{st.session_state.movie_context}

Use this information to answer questions about movies. If the user asks about a specific movie that isn't in your context, let them know you can search for it. Be conversational, enthusiastic about movies, and provide helpful recommendations."""

        hist = "\n".join([
            f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
            for msg in st.session_state.messages[-6:]
        ])
        
        full_pmt = f"{pmt}\n\nConversation History:\n{hist}\n\nUser: {user_message}\n\nAssistant:"
        
        res = model.generate_content(full_pmt)
        return res.text
        
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}. Please try again."

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me about movies... (e.g., Tell me about The Matrix)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                res = gen_resp(prompt)
                st.markdown(res)
                st.session_state.messages.append({"role": "assistant", "content": res})
            except Exception as e:
                err = "I'm sorry, but I encountered an error. Please try again."
                st.markdown(err)
                st.session_state.messages.append({"role": "assistant", "content": err})