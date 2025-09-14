import pickle
import streamlit as st
import requests
from streamlit_lottie import st_lottie


API_KEY = "5f7a6e8268da566eed84b43273c332bb"


movies = pickle.load(open("movie_list.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))


st.set_page_config(
    page_title="🎬 CineVerse",
    page_icon="🎥",
    layout="wide"
)


def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


lottie_background = load_lottie_url(
    "https://assets2.lottiefiles.com/packages/lf20_j1adxtyb.json"
)
st_lottie(lottie_background, speed=1, height=300, key="background")


st.markdown("""
<style>
body {
    background-color: #0f0f0f;
    color: #fff;
}
h1 {
    color: #e50914;
    text-align: center;
    text-shadow: 0px 0px 10px #e50914;
}
.movie-card {
    background-color: #1c1c1c;
    border-radius: 15px;
    padding: 10px;
    margin: 10px;
    text-align: center;
    transition: transform 0.5s ease, box-shadow 0.5s ease;
    opacity: 0;
    animation: fadeIn 0.7s forwards;
}
@keyframes fadeIn {
    to { opacity: 1; }
}
.movie-card:hover {
    transform: scale(1.08);
    box-shadow: 0px 0px 35px rgba(229,9,20,0.8);
}
.movie-poster {
    border-radius: 10px;
    width: 180px;
    height: 270px;
    object-fit: cover;
}
.footer {
    text-align: center;
    padding: 20px;
    font-size: 16px;
    color: #aaa;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🎬 CineVerse </h1>", unsafe_allow_html=True)
st.markdown("### Discover cinematic experiences tailored for you 🍿", unsafe_allow_html=True)


def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US&append_to_response=videos"
    data = requests.get(url).json()
    
    poster_url = "https://image.tmdb.org/t/p/w500" + data.get("poster_path","") \
                 if data.get("poster_path") else "https://via.placeholder.com/180x270?text=No+Poster"
    rating = data.get("vote_average","N/A")
    overview = data.get("overview","No description available.")
    release_date = data.get("release_date","N/A")
    genres = [g["name"] for g in data.get("genres",[])]
    trailer_url = None
    if "videos" in data and "results" in data["videos"]:
        for vid in data["videos"]["results"]:
            if vid["site"]=="YouTube" and vid["type"]=="Trailer":
                trailer_url = f"https://www.youtube.com/watch?v={vid['key']}"
                break
    return poster_url, rating, overview, trailer_url, release_date, genres

def recommend(movie):
    idx = movies[movies['title']==movie].index[0]
    distances = sorted(list(enumerate(similarity[idx])), reverse=True, key=lambda x:x[1])
    recommendations = []
    for i in distances[1:10]:
        movie_id = movies.iloc[i[0]].movie_id
        title = movies.iloc[i[0]].title
        poster, rating, overview, trailer, release_date, genres = fetch_movie_details(movie_id)
        recommendations.append((title, poster, rating, overview, trailer, release_date, genres))
        if len(recommendations) == 5:
            break
    return recommendations

def fetch_trending():
    url = f"https://api.themoviedb.org/3/trending/movie/week?api_key={API_KEY}"
    data = requests.get(url).json()
    trending = []
    for movie in data.get("results", [])[:10]:
        movie_id = movie["id"]
        title = movie["title"]
        poster, rating, overview, trailer, release_date, genres = fetch_movie_details(movie_id)
        trending.append((title, poster, rating, overview, trailer, release_date, genres))
    return trending


selected_movie = st.selectbox("🔎 Search for a movie", movies['title'].tolist())


if selected_movie:
    st.markdown("<h2>🔮 Recommended Movies</h2>", unsafe_allow_html=True)
    recs = recommend(selected_movie)
    cols = st.columns(5)
    
    for idx, (title, poster, rating, overview, trailer, release_date, genres) in enumerate(recs):
        with cols[idx]:
            st.markdown(f"""
            <div class="movie-card">
                <img src="{poster}" class="movie-poster">
                <h4>{title}</h4>
                <p>⭐ {rating}/10</p>
                <p style="font-size:12px; color:#bbb;">{overview[:100]}...</p>
                <p style="font-size:11px; color:#999;">Genres: {', '.join(genres)}</p>
                <p style="font-size:11px; color:#999;">Release: {release_date}</p>
                {f"<a href='{trailer}' target='_blank'>▶ Watch Trailer</a>" if trailer else ""}
            </div>
            """, unsafe_allow_html=True)


st.markdown("<h2>🔥 Trending This Week</h2>", unsafe_allow_html=True)
trending_movies = fetch_trending()
for i in range(0, len(trending_movies), 5):
    cols = st.columns(5)
    for idx, (title, poster, rating, overview, trailer, release_date, genres) in enumerate(trending_movies[i:i+5]):
        with cols[idx]:
            st.markdown(f"""
            <div class="movie-card">
                <img src="{poster}" class="movie-poster">
                <h4>{title}</h4>
                <p>⭐ {rating}/10</p>
                <p style="font-size:12px; color:#bbb;">{overview[:100]}...</p>
                <p style="font-size:11px; color:#999;">Genres: {', '.join(genres)}</p>
                <p style="font-size:11px; color:#999;">Release: {release_date}</p>
                {f"<a href='{trailer}' target='_blank'>▶ Watch Trailer</a>" if trailer else ""}
            </div>
            """, unsafe_allow_html=True)


st.markdown("<div class='footer'>🎬 Made by Abhiram | CineVerse 2025</div>", unsafe_allow_html=True)
