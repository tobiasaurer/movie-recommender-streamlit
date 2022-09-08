import streamlit as st
import pandas as pd

# DATA:
movies = pd.read_csv('https://raw.githubusercontent.com/tobiasaurer/recommender-systems/main/movie_data/movies.csv')
ratings = pd.read_csv('https://raw.githubusercontent.com/tobiasaurer/recommender-systems/main/movie_data/ratings.csv')

# clean titles column by moving "The" to the beginning of the string
# # this makes it more searchable for users
movies.loc[lambda df: df["title"].str.contains(", The", regex=True), 'title'] = 'The ' + movies['title']
movies.loc[lambda df: df["title"].str.contains(", The", regex=True), 'title'] = movies['title'].str.replace(", The", '', regex=True)

# INSTRUCTIONS:
st.title("Popularity-Based Recommender")
st.write("""
### Instructions
Move the slider to the desired number of recommendations you wish to receive.  
Afterwards, simply click the "Get Recommendations" button to receive recommendations based on the most popular movies in our database.  
  
__Optional__: You can narrow down the recommendations by picking one or several genre(s).  
However, the more genres you choose, the fewer movies will be recommended.
""")

# FUNCTIONS:

def get_popular_recommendations(n, genres):
    return (
        ratings
            .groupby('movieId')
            .agg(avg_rating = ('rating', 'mean'), num_ratings = ('rating', 'count'))
            .merge(movies, on='movieId')
            .assign(combined_rating = lambda x: x['avg_rating'] * x['num_ratings']**0.5)
            [lambda df: df["genres"].str.contains(genres, regex=True)]
            .sort_values('combined_rating', ascending=False)
            .head(n)
            [['title', 'avg_rating', 'genres']]
    )

def transform_genre_to_regex(genres):
    regex = ""
    for genre in genres:
        regex += f"(?=.*{genre})"
    return regex

# USER INPUT:
number_of_recommendations = st.slider("Number of recommendations", 1, 10, 5)

genre_list = set([inner for outer in movies.genres.str.split('|') for inner in outer])
genres = st.multiselect('Optional: Select one or more genres', genre_list, default=None, key=None, help=None, on_change=None, args=None, kwargs=None, disabled=False)
genres_regex = transform_genre_to_regex(genres)

# EXECUTION:
if st.button("Get Recommendations"):
    st.write(get_popular_recommendations(number_of_recommendations, genres_regex))