import requests
import streamlit as st

st.title("Lab03 Phase I")

url = "http://www.omdbapi.com/?apikey=89d15140&"

st.text("---------------------------------")
st.title("🎬 Movie Rating Explorer")


st.text("---------------------------------")

st.header("Keigo")

if "movies" not in st.session_state:
    st.session_state.movies = []

if "result" not in st.session_state:
    st.session_state.result = []

kw = st.text_input("Enter a keyword:", "Batman")
submitted = st.button("Search")

sorted_by = st.selectbox(
    "Sorted By:",
    [
        "IMDB Rating (High → Low)",
        "Released Year (Old → New)",
        "Released Year (New → Old)",
        "Title (A → Z)",
    ],
)

if submitted:
    res = requests.get(f"{url}&s={kw}")
    data = res.json()

    if data["Response"] == "True":
        ret = []
        for m in data["Search"]:
            title = m["Title"]
            detail = requests.get(f"{BASE_URL}?apikey={API_KEY}&t={title}").json()
            
            # print(detail["imdbRating"])
            
            if detail["imdbRating"] == "N/A":
                rating = 0.0
            else:
                rating = float(detail["imdbRating"])
            
            year = int(detail["Year"][:4])
            
            ret.append({
                "Title": title,
                "Poster": m["Poster"],
                "Rating": rating,
                "Year": year,
                "Detail": detail
            })
            
        st.session_state.result = ret
        st.session_state.kw = kw
    else:
        st.error("No results found. Try another keyword.")

if st.session_state.result:
    st.success(f"Showing results for '{st.session_state.get('kw','(previous search)')}'")

    result = st.session_state.result.copy()

    if sorted_by == "IMDB Rating (High → Low)":
        result = sorted(result, key=lambda x: x["Rating"], reverse=True)
    elif sorted_by == "Released Year (Old → New)":
        result = sorted(result, key=lambda x: x["Year"])
    elif sorted_by == "Released Year (New → Old)":
        result = sorted(result, key=lambda x: x["Year"], reverse=True)
    elif sorted_by == "Title (A → Z)":
        result = sorted(result, key=lambda x: x["Title"])

    for m in result:
        title = m["Title"]
        poster = m["Poster"]
        detail = m["Detail"]

        with st.container():
            l, r = st.columns([1, 3])
            with l:
                st.image(poster)
            with r:
                st.markdown(f"### 🎬 {title}")
                st.write(f"**Year:** {detail["Year"]}")
                st.write(f"**Director:** {detail["Director"]}")
                st.write(f"**Genre:** {detail["Genre"]}")
                st.write(f"**IMDB Rating:** ⭐ {detail["imdbRating"]} / 10")
                st.caption(detail.get("Plot","No plot available."))
            st.divider()