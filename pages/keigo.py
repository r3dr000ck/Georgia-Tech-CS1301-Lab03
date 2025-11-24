import streamlit as st
import requests
import google.generativeai as genai
import os

# ページ設定
st.set_page_config(page_title="Movie Chatbot", page_icon="🎬")

# CSSで固定入力欄とスクロール可能なチャットエリアを実装
st.markdown("""
<style>
    /* メインコンテナの調整 */
    .main {
        padding-bottom: 120px;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* チャットエリアをスクロール可能に */
    .chat-container {
        max-width: 900px;
        margin: 0 auto;
        height: calc(100vh - 280px);
        overflow-y: auto;
        padding: 20px;
        margin-bottom: 10px;
    }
    
    /* 入力欄を画面下部に固定 */
    .fixed-input {
        position: fixed;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        max-width: 900px;
        width: 90%;
        background-color: white;
        padding: 15px 20px;
        border-top: 2px solid #e0e0e0;
        z-index: 999;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
    }
    
    /* ダークモード対応 */
    [data-theme="dark"] .fixed-input {
        background-color: #0e1117;
        border-top: 2px solid #262730;
    }
    
    /* Streamlitのデフォルトパディングを調整 */
    .stChatMessage {
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    /* タイトルエリアも中央寄せ */
    .block-container {
        max-width: 900px;
        padding-left: 2rem;
        padding-right: 2rem;
        padding-bottom: 0;
    }
    
    /* 不要な余白を削除 */
    .main .block-container {
        padding-bottom: 0 !important;
    }
    
    /* フッターを非表示 */
    footer {
        display: none;
    }
    
    /* Streamlitのデフォルトマージンを調整 */
    .element-container {
        margin-bottom: 0;
    }
</style>
""", unsafe_allow_html=True)

# APIキーの設定
OMDB_API_KEY = os.getenv("OMDB_API_KEY", "YOUR_OMDB_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")

# Gemini APIの初期化
genai.configure(api_key=GEMINI_API_KEY)

# タイトル
st.title("🎬 Movie Chatbot")
st.markdown("Ask me anything about movies! I can search for movie information and have a conversation with you.")

# セッション状態の初期化
if "messages" not in st.session_state:
    st.session_state.messages = []

if "movie_context" not in st.session_state:
    st.session_state.movie_context = ""

if "processing" not in st.session_state:
    st.session_state.processing = False

# OMDBから映画情報を取得する関数
def fetch_movie_data(query):
    """OMDBから映画情報を取得"""
    try:
        # 映画タイトルで検索
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

# Gemini APIで応答を生成する関数
def generate_gemini_response(user_message):
    """Gemini APIを使って応答を生成"""
    try:
        # モデルの初期化
        model = genai.GenerativeModel('gemini-pro')
        
        # システムプロンプトの作成
        system_prompt = f"""You are a helpful movie expert chatbot. You have access to the following movie information from OMDB:

{st.session_state.movie_context}

Use this information to answer questions about movies. If the user asks about a specific movie that isn't in your context, let them know you can search for it. Be conversational, enthusiastic about movies, and provide helpful recommendations."""

        # 会話履歴を含むプロンプトの作成
        conversation_history = "\n".join([
            f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
            for msg in st.session_state.messages[-6:]  # 最新6件のメッセージのみ使用
        ])
        
        full_prompt = f"{system_prompt}\n\nConversation History:\n{conversation_history}\n\nUser: {user_message}\n\nAssistant:"
        
        # 応答を生成
        response = model.generate_content(full_prompt)
        return response.text
        
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}. Please try again."

# 映画タイトルを抽出する簡易関数
def extract_movie_title(message):
    """メッセージから映画タイトルを抽出（簡易版）"""
    keywords = ["tell me about", "information about", "what is", "search for", "find"]
    message_lower = message.lower()
    
    for keyword in keywords:
        if keyword in message_lower:
            # キーワードの後の部分を抽出
            start_idx = message_lower.find(keyword) + len(keyword)
            potential_title = message[start_idx:].strip().strip('?".')
            if potential_title:
                return potential_title
    return None

# チャット履歴を表示（スクロール可能なエリア）
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
st.markdown('</div>', unsafe_allow_html=True)

# 画面下部に固定された入力欄
st.markdown('<div class="fixed-input">', unsafe_allow_html=True)
input_container = st.container()
with input_container:
    col1, col2 = st.columns([6, 1])
    
    with col1:
        user_input = st.text_input(
            "Ask me about movies...",
            key="user_input",
            placeholder="e.g., Tell me about The Matrix",
            label_visibility="collapsed",
            disabled=st.session_state.processing
        )
    
    with col2:
        send_button = st.button("Send", use_container_width=True, disabled=st.session_state.processing)

st.markdown('</div>', unsafe_allow_html=True)

# メッセージ送信処理
if send_button and user_input and not st.session_state.processing:
    st.session_state.processing = True
    
    # ユーザーメッセージを追加
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # 映画タイトルを抽出して検索
    movie_title = extract_movie_title(user_input)
    if movie_title:
        with st.spinner("Searching for movie information..."):
            movie_info, movie_data = fetch_movie_data(movie_title)
            if movie_info:
                st.session_state.movie_context = movie_info
    
    # Gemini APIで応答を生成
    with st.spinner("Thinking..."):
        try:
            bot_response = generate_gemini_response(user_input)
            
            # ボットの応答を追加
            st.session_state.messages.append({"role": "assistant", "content": bot_response})
        
        except Exception as e:
            error_message = f"I apologize, but I encountered an error. Please try again."
            st.session_state.messages.append({"role": "assistant", "content": error_message})
    
    st.session_state.processing = False
    # 入力欄をクリア（再実行で実現）
    st.rerun()

# サイドバーに使い方を表示
with st.sidebar:
    st.header("How to use")
    st.markdown("""
    1. Type your question about movies in the text box at the bottom
    2. Click 'Send' or press Enter
    3. Wait for the chatbot to respond
    4. Scroll through the chat history
    
    **Example questions:**
    - Tell me about The Matrix
    - What is the plot of Inception?
    - Search for Interstellar
    - Who directed The Godfather?
    """)
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.session_state.movie_context = ""
        st.rerun()