import requests
import streamlit as st

st.title("Lab03 Phase I")

url = "http://www.omdbapi.com/?apikey=89d15140&"

st.text("---------------------------------")
st.title("🎬 Movie Rating Explorer")


st.text("---------------------------------")

st.header("Keigo")
m_data = requests.get(url + "t=Inception").json()
st.image(m_data["Poster"], width=200)

