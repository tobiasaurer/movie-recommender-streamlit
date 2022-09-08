import streamlit as st
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# DATA:
movies = pd.read_csv('https://raw.githubusercontent.com/tobiasaurer/movie-recommender-streamlit/main/data/movies.csv')
ratings = pd.read_csv('https://raw.githubusercontent.com/tobiasaurer/movie-recommender-streamlit/main/data/ratings.csv')
links = pd.read_csv('https://raw.githubusercontent.com/tobiasaurer/movie-recommender-streamlit/main/data/links.csv')

# clean titles column by moving "The" and "A" to the beginning of the string
# this makes it more searchable for users
movies.loc[lambda df: df["title"].str.contains(", The", regex=True), 'title'] = 'The ' + movies['title']
movies.loc[lambda df: df["title"].str.contains(", The", regex=True), 'title'] = movies['title'].str.replace(", The", '', regex=True)

movies.loc[lambda df: df["title"].str.contains(", A", regex=True), 'title'] = 'A ' + movies['title']
movies.loc[lambda df: df["title"].str.contains(", A", regex=True), 'title'] = movies['title'].str.replace(", A", '', regex=True)

# create "database" to use for recommendations
user_item_matrix = (
                    ratings
                        .merge(movies, on='movieId')[['title', 'rating', 'userId']]
                        .pivot_table(index='userId', columns='title', values='rating')
                        .fillna(0)
                    )

similarities_users = pd.DataFrame(cosine_similarity(user_item_matrix),
                                  index=user_item_matrix.index,
                                  columns=user_item_matrix.index)

# INSTRUCTIONS:
st.title("User-Based Recommender")
st.write("""
### Instructions
Type in the user-ID you want to receive recommendations for.  
Move the slider to the desired number of recommendations you wish to receive.  
Afterwards, simply click the "Get Recommendations" button to receive recommendations that are most suitable for the given user.  
  
__Optional__: You can narrow down the recommendations by picking one or several genre(s).  
However, the more genres you choose, the fewer movies will be recommended.
""")

# FUNCTIONS:

def get_user_recommendations(user_id, n, genres):
    
    user_id = int(user_id)
    # calculate weights for ratings
    weights = similarities_users.loc[similarities_users.index != user_id, user_id] / sum(similarities_users.loc[similarities_users.index != user_id, user_id])
    
    # get unwatched movies for recommendations
    unwatched_movies = (
        user_item_matrix
            .loc[user_item_matrix.index != user_id, user_item_matrix.loc[user_id,:] == 0]
            .T
        )

    # compute weighted averages and return the n movies with the highest predicted ratings
    weighted_averages = pd.DataFrame(unwatched_movies.dot(weights), columns = ["predicted_rating"])
    recommendations = (
        weighted_averages
            .sort_values("predicted_rating", ascending=False)
            .merge(movies, how= 'left', left_index = True, right_on = 'title')
            [lambda df: df["genres"].str.contains(genres, regex=True)]
            .head(n)
    )

    return recommendations[['title', 'genres']]

def transform_genre_to_regex(genres):
    regex = ""
    for genre in genres:
        regex += f"(?=.*{genre})"
    return regex

# USER INPUT:
user_id_input = st.text_input('User-ID')

number_of_recommendations = st.slider("Number of recommendations", 1, 10, 5)

genre_list = set([inner for outer in movies.genres.str.split('|') for inner in outer])
genres = st.multiselect('Optional: Select one or more genres', genre_list, default=None, key=None, help=None, on_change=None, args=None, kwargs=None, disabled=False)
genres_regex = transform_genre_to_regex(genres)

# EXECUTION:
if st.button("Get Recommendations"):
    st.write(get_user_recommendations(user_id_input, number_of_recommendations, genres_regex))