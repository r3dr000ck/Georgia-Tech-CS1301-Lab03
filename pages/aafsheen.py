import google.generativeai as genai
import requests

GEMINI_API_KEY = "AIzaSyCQNy4vivWIVBlvT1hqRzz2VXs5nLuvPMU"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

url = "http://www.omdbapi.com/?apikey=89d15140&"

# Example
import streamlit as st
import requests
import google.generativeai as genai

st.title("🎞️ AI Movie Deep Dive")
st.write("Enter one or two movie titles and get an AI-generated analysis!")

# Configure Gemini
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

OMDB = st.secrets["OMDB_API_KEY"]
URL = f"http://www.omdbapi.com/?apikey={OMDB}&"

# --------------------------------
# --------------------------------
movie1 = st.text_input("Movie 1 Title:", "")
movie2 = st.text_input("Movie 2 Title (optional):", "")

analysis_type = st.selectbox(
    "What should the AI create?",
    [
        "Character Analysis",
        "Plot Summary",
        "Funny Rewrite",
        "Theme Explanation",
        "Director Style Breakdown",
        "Movie Comparison (if 2 movies)"
    ]
)

# --------------------------------
# --------------------------------
def get_movie(title):
    if not title:
        return None
    data = requests.get(f"{URL}&t={title}").json()
    if data.get("Response") == "False":
        return None
    return data

# --------------------------------
# BUTTON
# --------------------------------
if st.button("Generate Analysis"):
    data1 = get_movie(movie1)
    data2 = get_movie(movie2) if movie2 else None

    if not data1:
        st.error("Movie 1 not found. Check your spelling.")
        st.stop()

    st.subheader("Movie Information (from OMDb)")

    # show movie 1
    st.write(f"### 🎬 {data1['Title']} ({data1['Year']})")
    st.write(f"**Genre:** {data1['Genre']}")
    st.write(f"**Director:** {data1['Director']}")
    st.write(f"**Plot:** {data1['Plot']}")
    st.write("---")

    # show movie 2 if exists
    if data2:
        st.write(f"### 🎬 {data2['Title']} ({data2['Year']})")
        st.write(f"**Genre:** {data2['Genre']}")
        st.write(f"**Director:** {data2['Director']}")
        st.write(f"**Plot:** {data2['Plot']}")
        st.write("---")

    # --------------------------------

    # --------------------------------
    movie_info = f"""
    MOVIE 1:
    Title: {data1['Title']}
    Year: {data1['Year']}
    Genre: {data1['Genre']}
    Director: {data1['Director']}
    Plot: {data1['Plot']}
    """

    if data2:
        movie_info += f"""

        MOVIE 2:
        Title: {data2['Title']}
        Year: {data2['Year']}
        Genre: {data2['Genre']}
        Director: {data2['Director']}
        Plot: {data2['Plot']}
        """

    # --------------------------------
    # GEMINI PROMPT
    # --------------------------------
    prompt = f"""
    You are a helpful movie expert.

    Create a **{analysis_type}** using only the movie information below:

    {movie_info}

    Make the explanation clear and interesting.
    """

    # --------------------------------
    # CALL GEMINI
    # --------------------------------
    try:
        response = model.generate_content(prompt)
        st.subheader("📜 AI-Generated Analysis")
        st.write(response.text)

    except Exception as e:
        st.error("Something went wrong with Gemini.")
        st.text(str(e))
