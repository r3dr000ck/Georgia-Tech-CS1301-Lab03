import requests
import streamlit as st

st.title("Movie Info Page")

url = "http://www.omdbapi.com/?apikey=89d15140&"


st.header("Posters")
m_data = requests.get(url + "t=Inception").json()
st.image(m_data["Poster"], width=200)