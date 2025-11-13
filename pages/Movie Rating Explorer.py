import requests
import streamlit as st

# https://georgia-tech-cs1301-lab03-nzbcbjgrjwtsbmztj6nesp.streamlit.app/

st.title("🎬 Movie Rating Explorer")

url = "http://www.omdbapi.com/?apikey=89d15140&"

st.header("📊 Rating Comparison")

SERIES = {
    "Middle Earth (LOTR + Hobbit)": [
        "The Lord of the Rings: The Fellowship of the Ring",
        "The Lord of the Rings: The Two Towers",
        "The Lord of the Rings: The Return of the King",
        "The Hobbit: An Unexpected Journey",
        "The Hobbit: The Desolation of Smaug",
        "The Hobbit: The Battle of the Five Armies",
    ],

    "Christopher Nolan": [
        "Inception",
        "Interstellar",
        "The Dark Knight",
        "The Dark Knight Rises",
        "Batman Begins",
        "Tenet",
        "Dunkirk",
        "Memento",
        "The Prestige",
        "Insomnia",
    ],

    "Mission Impossible": [
        "Mission: Impossible",
        "Mission: Impossible II",
        "Mission: Impossible III",
        "Mission: Impossible - Ghost Protocol",
        "Mission: Impossible - Rogue Nation",
        "Mission: Impossible - Fallout",
        "Mission: Impossible - Dead Reckoning Part One",
    ],

    "Star Wars (Skywalker Saga)": [
        "Star Wars: Episode I - The Phantom Menace",
        "Star Wars: Episode II - Attack of the Clones",
        "Star Wars: Episode III - Revenge of the Sith",
        "Star Wars: Episode IV - A New Hope",
        "Star Wars: Episode V - The Empire Strikes Back",
        "Star Wars: Episode VI - Return of the Jedi",
        "Star Wars: Episode VII - The Force Awakens",
        "Star Wars: Episode VIII - The Last Jedi",
        "Star Wars: Episode IX - The Rise of Skywalker",
    ],
    "DC Universe": [
        "Man of Steel",
        "Batman v Superman: Dawn of Justice",
        "Wonder Woman",
        "Aquaman",
        "Justice League",
        "Shazam!",
        "The Flash",
    ],
    "Marvel Cinematic Universe": [
        "Iron Man",
        "Captain America: The First Avenger",
        "The Avengers",
        "Black Panther",
        "Avengers: Endgame",
    ]
}

series_show = st.multiselect("Select Series",SERIES.keys())

@st.cache_data
def fetch_detail(title):
    detail = requests.get(f"{url}&t={title}").json()

    if detail["Response"] == "False":
        return None
    
    rating = 0.0 if detail["imdbRating"] == "N/A" else float(detail["imdbRating"])
    return {
        "Title": title,
        "Rating": rating,
        "Year": detail.get("Year", "N/A"),
        "Director": detail.get("Director", "N/A"),
        "Genre": detail.get("Genre", "N/A"),
    }

movies = []

for series in series_show:
    for title in SERIES[series]:
        detail = fetch_detail(title)
        if detail:
            detail["Series"] = series
            movies.append(detail)

if series_show:
    min_rating = st.slider("Filter by minimum IMDB rating:", 0.0, 10.0, 0.0, 0.5)
    
    filtered_movies = [m for m in movies if m["Rating"] >= min_rating]
    
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
    st.error("Please select a series!")

st.header("🔍Movie Search")

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
                if poster and poster != "N/A":
                    st.image(poster)
                else:
                    st.info("No poster available.")
            with r:
                st.markdown(f"### 🎬 {title}")
                st.write(f"**Year:** {detail["Year"]}")
                st.write(f"**Director:** {detail["Director"]}")
                st.write(f"**Genre:** {detail["Genre"]}")
                st.write(f"**IMDB Rating:** ⭐ {detail["imdbRating"]} / 10")
                st.caption(detail.get("Plot","No plot available."))
            st.divider()

