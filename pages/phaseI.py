import requests
import streamlit as st

st.title("Lab03 Phase I")

url = "http://www.omdbapi.com/?apikey=89d15140&"

st.text("---------------------------------")
st.title("🎬 Movie Rating Explorer")
st.header("📊 Rating Comparison")

if "result" not in st.session_state:
    st.session_state.result = []

if st.session_state.result:
    min_rating = st.slider("Filter by minimum IMDB rating:", 0.0, 10.0, 0.0, 0.5)
    
    filtered_movies = [movie for movie in st.session_state.result if movie["Rating"] >= min_rating]
    
    if filtered_movies:
        chart_data = {}
        for movie in filtered_movies:
            short_title = movie["Title"][:20] + "..." if len(movie["Title"]) > 20 else movie["Title"]
            chart_data[short_title] = movie["Rating"]
        
        st.bar_chart(chart_data)
        
        st.subheader("📈 Quick Stats")
        ratings = [movie["Rating"] for movie in filtered_movies]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Rating", f"{sum(ratings)/len(ratings):.1f}")
        with col2:
            st.metric("Highest Rating", f"{max(ratings):.1f}")
        with col3:
            st.metric("Movies", len(filtered_movies))
    else:
        st.warning(f"No movies found with rating {min_rating} or higher")
else:
    st.info("Search for movies to see the rating chart!")

st.text("---------------------------------")

st.header("Movie Search")

if "movies" not in st.session_state:
    st.session_state.movies = []

if "search" not in st.session_state:
    st.session_state.search = []

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
            detail = requests.get(f"{url}&t={title}").json()
            
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
            
        st.session_state.search = ret
        st.session_state.kw = kw
    else:
        st.error("No results found. Try another keyword.")

if st.session_state.search:
    st.success(f"Showing results for '{st.session_state.get('kw','(previous search)')}'")

    search = st.session_state.search.copy()

    if sorted_by == "IMDB Rating (High → Low)":
        search = sorted(search, key=lambda x: x["Rating"], reverse=True)
    elif sorted_by == "Released Year (Old → New)":
        search = sorted(search, key=lambda x: x["Year"])
    elif sorted_by == "Released Year (New → Old)":
        search = sorted(search, key=lambda x: x["Year"], reverse=True)
    elif sorted_by == "Title (A → Z)":
        search = sorted(search, key=lambda x: x["Title"])

    for m in search:
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

