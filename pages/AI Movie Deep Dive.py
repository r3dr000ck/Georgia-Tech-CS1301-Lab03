import streamlit as st
import requests
import google.generativeai as genai

GEMINI_API_KEY = "AIzaSyCQNy4vivWIVBlvT1hqRzz2VXs5nLuvPMU"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

OMDB = "89d15140"
URL = f"http://www.omdbapi.com/?apikey={OMDB}&"

st.title("🎞️ AI Movie Deep Dive")
st.write("Enter one or two movie titles and get an AI-generated analysis!")

m1 = st.text_input("Movie 1 Title:", "")
m2 = st.text_input("Movie 2 Title (optional):", "")

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

def get_movie(title):
    if not title:
        return None
    data = requests.get(f"{URL}&t={title}").json()
    if data.get("Response") == "False":
        return None
    return data

if st.button("Generate Analysis"):
    d1 = get_movie(m1)
    d2 = get_movie(m2) if m2 else None

    if not d1:
        st.error("Movie 1 not found. Check your spelling.")
        st.stop()

    movie_info = f"""
    MOVIE 1:
    Title: {['Title']}
    Year: {d1['Year']}
    Genre: {d1['Genre']}
    Director: {d1['Director']}
    Plot: {d1['Plot']}
    """

    if d2:
        movie_info += f"""

        MOVIE 2:
        Title: {d2['Title']}
        Year: {d2['Year']}
        Genre: {d2['Genre']}
        Director: {d2['Director']}
        Plot: {d2['Plot']}
        """

    pmt = f"""
    You are a helpful movie expert.

    Create a **{analysis_type}** using only the movie information below:

    {movie_info}

    Make the explanation clear and interesting.
    """

    try:
        response = model.generate_content(pmt)
        st.subheader("📜 AI-Generated Analysis")
        st.write(response.text)

    except Exception as e:
        st.error("Something went wrong with Gemini.")
        st.text(str(e))