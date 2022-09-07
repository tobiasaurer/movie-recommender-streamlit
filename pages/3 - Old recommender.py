import streamlit as st
import pandas as pd


st.title("Movie Recommender")
 
st.write("""
### Instructions
Type in a movie title with the release year in brackets (e.g. "The Matrix (1999)"), choose the number of recommendations you wish, and the app will recommend movies based on your chosen movie.\n\n 
The recommendation process will take ca. 15 seconds. 
""")

chosen_movie = st.text_input("Movie title and release year")
number_of_recommendations = st.slider("Number of recommendations", 1, 10, 5)

movies = pd.read_csv('https://raw.githubusercontent.com/tobiasaurer/recommender-systems/main/movie_data/movies.csv')
ratings = pd.read_csv('https://raw.githubusercontent.com/tobiasaurer/recommender-systems/main/movie_data/ratings.csv')

all_ratings = ratings.merge(movies, on='movieId')[['title', 'rating', 'userId']]
all_ratings_pivoted = all_ratings.pivot_table(index='userId', columns='title', values='rating')

def get_recommendations_for_movie(movie_name, n):
    
    eligible_movies = []

    for movie in all_ratings_pivoted.columns:
        nr_shared_ratings = all_ratings_pivoted.loc[all_ratings_pivoted[movie_name].notnull() & all_ratings_pivoted[movie].notnull(), [movie_name, movie]].count()[0]
        if nr_shared_ratings >= 10:
            eligible_movies.append(movie)

    return (
        all_ratings_pivoted
            [eligible_movies]
            .corrwith(all_ratings_pivoted[movie_name]).sort_values(ascending=False)[1:n+1]
            .index
    )

if st.button("Recommend"):
    
    recommendations = get_recommendations_for_movie(chosen_movie, number_of_recommendations)

    st.write("Recommendations for", chosen_movie)
    st.write(recommendations)