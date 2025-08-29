import pickle
import streamlit as st
import requests

# ─── OMDb API Key ───
OMDB_API_KEY = "b02902db"  # Replace with your valid key

# ─── Cached Poster Fetch Function ───
@st.cache_data(show_spinner=False)
def fetch_poster(movie_name):
    """Fetch movie poster from OMDb, return placeholder if fails"""
    try:
        url = f"https://www.omdbapi.com/?t={movie_name}&apikey={OMDB_API_KEY}"
        response = requests.get(url, timeout=20)  # Increase timeout

        # Handle API errors
        if response.status_code == 401:
            st.warning(f"Unauthorized: Check your OMDb API key!")
            return "https://via.placeholder.com/300x450?text=No+Poster"
        elif response.status_code != 200:
            return "https://via.placeholder.com/300x450?text=No+Poster"

        data = response.json()
        if data.get("Response") == "True":
            poster = data.get("Poster")
            if poster and poster != "N/A":
                return poster
            else:
                return "https://via.placeholder.com/300x450?text=No+Poster"
        else:
            return "https://via.placeholder.com/300x450?text=No+Poster"

    except requests.exceptions.Timeout:
        return "https://via.placeholder.com/300x450?text=No+Poster"
    except requests.exceptions.RequestException:
        return "https://via.placeholder.com/300x450?text=No+Poster"

# ─── Recommendation Logic ───
def recommend(movie):
    idx = movies[movies['title'] == movie].index[0]
    distances = sorted(enumerate(similarity[idx]), reverse=True, key=lambda x: x[1])
    
    names, posters = [], []
    for i in distances[1:6]:  # Top 5 recommendations
        title = movies.iloc[i[0]].title
        names.append(title)
        posters.append(fetch_poster(title))
    return names, posters

# ─── Streamlit Interface ───
st.set_page_config(page_title="Movie Recommender", layout="wide")
st.header("🎬 Movie Recommender System")

# Load data
movies = pickle.load(open("movie_list.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# Movie selection dropdown
selected = st.selectbox("Select a movie:", movies["title"].values)

# Show recommendations
if st.button("Show Recommendation"):
    rec_names, rec_posters = recommend(selected)
    
    # Use narrower columns for smaller images
    cols = st.columns([1, 1, 1, 1, 1])  # 5 equal columns
    for col, name, poster in zip(cols, rec_names, rec_posters):
        with col:
            # Smaller image width
            st.image(poster, width=220)
            st.markdown(
                f"<p style='color:#FF5733; font-weight:bold; text-align:center;'>{name}</p>",
                unsafe_allow_html=True
            )
