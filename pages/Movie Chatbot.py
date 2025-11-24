import streamlit as st
import requests
import google.generativeai as genai

OMDB_API_KEY = "89d15140"
GEMINI_API_KEY = "AIzaSyCQNy4vivWIVBlvT1hqRzz2VXs5nLuvPMU"

genai.configure(api_key=GEMINI_API_KEY)

st.markdown("""
<style>
    /* 全体のレイアウト */
    .main {
        padding-top: 2rem;
        padding-bottom: 1rem;
    }
    
    /* タイトルエリア */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 1rem;
    }
    
    /* チャットメッセージのスタイル */
    .stChatMessage {
        padding: 1rem;
        margin-bottom: 0.5rem;
    }
    
    /* ユーザーメッセージ */
    .stChatMessage[data-testid="user"] {
        background-color: #f0f2f6;
    }
    
    /* アシスタントメッセージ */
    .stChatMessage[data-testid="assistant"] {
        background-color: #ffffff;
    }
    
    [data-theme="dark"] .stChatMessage[data-testid="assistant"] {
        background-color: #1e1e1e;
    }
    
    /* チャット入力欄のスタイル */
    .stChatInput {
        position: sticky;
        bottom: 0;
        background-color: var(--background-color);
        padding-top: 1rem;
        padding-bottom: 1rem;
        z-index: 100;
    }
    
    /* フッターを非表示 */
    footer {
        visibility: hidden;
    }
    
    /* メニューを非表示 */
    #MainMenu {
        visibility: hidden;
    }
    
    /* タイトルのスタイル */
    h1 {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    
    /* 説明文のスタイル */
    .stMarkdown p {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎬 Movie Chatbot")
st.markdown("Ask me anything about movies! I can search for movie information and have a conversation with you.")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "movie_context" not in st.session_state:
    st.session_state.movie_context = ""

def fetch_movie_data(query):
    try:
        url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={query}"
        response = requests.get(url)
        data = response.json()
        
        if data.get("Response") == "True":
            movie_info = f"""
Movie Title: {data.get('Title', 'N/A')}
Year: {data.get('Year', 'N/A')}
Director: {data.get('Director', 'N/A')}
Actors: {data.get('Actors', 'N/A')}
Plot: {data.get('Plot', 'N/A')}
Genre: {data.get('Genre', 'N/A')}
IMDB Rating: {data.get('imdbRating', 'N/A')}
Runtime: {data.get('Runtime', 'N/A')}
"""
            return movie_info, data
        else:
            return None, None
    except Exception as e:
        st.error(f"Error fetching movie data: {str(e)}")
        return None, None

def generate_gemini_response(user_message):
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        system_prompt = f"""You are a helpful movie expert chatbot. You have access to the following movie information from OMDB:

{st.session_state.movie_context}

Use this information to answer questions about movies. If the user asks about a specific movie that isn't in your context, let them know you can search for it. Be conversational, enthusiastic about movies, and provide helpful recommendations."""

        conversation_history = "\n".join([
            f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
            for msg in st.session_state.messages[-6:]
        ])
        
        full_prompt = f"{system_prompt}\n\nConversation History:\n{conversation_history}\n\nUser: {user_message}\n\nAssistant:"
        
        response = model.generate_content(full_prompt)
        return response.text
        
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}. Please try again."

def extract_movie_title(message):
    keywords = ["tell me about", "information about", "what is", "search for", "find"]
    message_lower = message.lower()
    
    for keyword in keywords:
        if keyword in message_lower:
            start_idx = message_lower.find(keyword) + len(keyword)
            potential_title = message[start_idx:].strip().strip('?".')
            if potential_title:
                return potential_title
    return None

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me about movies... (e.g., Tell me about The Matrix)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    movie_title = extract_movie_title(prompt)
    if movie_title:
        with st.spinner("Searching for movie information..."):
            movie_info, movie_data = fetch_movie_data(movie_title)
            if movie_info:
                st.session_state.movie_context = movie_info
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                bot_response = generate_gemini_response(prompt)
                st.markdown(bot_response)
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
            except Exception as e:
                error_message = "I apologize, but I encountered an error. Please try again."
                st.markdown(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})
