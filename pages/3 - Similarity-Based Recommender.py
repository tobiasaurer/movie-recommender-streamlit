import streamlit as st
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import re

# DATA:
movies = pd.read_csv('https://raw.githubusercontent.com/tobiasaurer/recommender-systems/main/movie_data/movies.csv')
ratings = pd.read_csv('https://raw.githubusercontent.com/tobiasaurer/recommender-systems/main/movie_data/ratings.csv')

# clean titles column by moving "The" to the beginning of the string
# # this makes it more searchable for users
movies.loc[lambda df: df["title"].str.contains(", The", regex=True), 'title'] = 'The ' + movies['title']
movies.loc[lambda df: df["title"].str.contains(", The", regex=True), 'title'] = movies['title'].str.replace(", The", '', regex=True)

# create "database" to use for recommendations
movie_user_matrix = (
                ratings
                    .merge(movies, on='movieId')[['title', 'rating', 'userId']]
                    .pivot_table(index='title', columns='userId', values='rating')
                    .fillna(0)
                )
similarities_movies = pd.DataFrame(cosine_similarity(movie_user_matrix),
                                  index=movie_user_matrix.index,
                                  columns=movie_user_matrix.index)

# INSTRUCTIONS:
st.title("User-Based Recommender")
st.write("""
### Instructions
Type in the title of a movie for which you would like to receive similar recommendations.  
Move the slider to the desired number of recommendations you wish to receive.  
Afterwards, simply click the "Get Recommendations" button to receive recommendations that are most similar to the given movie.  
  
__Optional__: You can narrow down the recommendations by picking one or several genre(s).  
However, the more genres you choose, the fewer movies will be recommended.
""")

# FUNCTIONS:

def get_similar_recommendations(movie_title, n, genres):
    
    # select similarity for chosen movie
    similarities = pd.DataFrame(
        (similarities_movies.query("index != @movie_title")[movie_title] / sum(similarities_movies.query("index != @movie_title")[movie_title]))
        .sort_values(ascending= False))
 
    # exclude genres if necessary and return the n movies with the highest similarity
    recommendations = (
        similarities
            .merge(movies, how= 'left', left_index = True, right_on = 'title')
            [lambda df: df["genres"].str.contains(genres, regex=True)]
            .head(n)
            [['title', 'genres']]
            )

    return recommendations

def transform_genre_to_regex(genres):
    regex = ""
    for genre in genres:
        regex += f"(?=.*{genre})"
    return regex

def find_movie_title(user_input):
    title_list = movies.title.unique()
    
    r = re.compile(f".*{user_input}.*")
    result = []

    for title in title_list:
        match = r.findall(title)
        if match:
            result.append(match)
    
    return result[0][0]

# USER INPUT:
movie_title_raw = st.text_input('Movie Title')
movie_title = find_movie_title(movie_title_raw)

number_of_recommendations = st.slider("Number of recommendations", 1, 10, 5)

genre_list = set([inner for outer in movies.genres.str.split('|') for inner in outer])
genres = st.multiselect('Optional: Select one or more genres', genre_list, default=None, key=None, help=None, on_change=None, args=None, kwargs=None, disabled=False)
genres_regex = transform_genre_to_regex(genres)

# EXECUTION:
if st.button("Get Recommendations"):
    st.write(get_similar_recommendations(movie_title, number_of_recommendations, genres_regex))