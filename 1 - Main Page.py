import streamlit as st
import pandas as pd

st.markdown("# Introduction")
st.sidebar.markdown("# Introduction")

st.title("Movie Recommenders")
 
st.write("""
### Instructions
Check the Sidebar and choose a recommender that suits your purpose.  
""")

movies = pd.read_csv('https://raw.githubusercontent.com/tobiasaurer/recommender-systems/main/movie_data/movies.csv')
ratings = pd.read_csv('https://raw.githubusercontent.com/tobiasaurer/recommender-systems/main/movie_data/ratings.csv')

all_ratings = ratings.merge(movies, on='movieId')[['title', 'rating', 'userId']]
all_ratings_pivoted = all_ratings.pivot_table(index='userId', columns='title', values='rating')
