import streamlit as st
import pandas as pd
import re
import requests
import api_keys

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

# extract year from title and store it in new column
movies= movies.assign(year = lambda df_ : df_['title'].replace(r'(.*)\((\d{4})\)', r'\2', regex= True))
movies.year = pd.to_numeric(movies.year, errors= 'coerce').fillna(0).astype('int')

# INSTRUCTIONS:
st.title("Popularity-Based Recommender")

# FUNCTIONS:

def get_popular_recommendations(n, genres, time_range):
    recommendations = (
        ratings
            .groupby('movieId')
            .agg(avg_rating = ('rating', 'mean'), num_ratings = ('rating', 'count'))
            .merge(movies, on='movieId')
            .assign(combined_rating = lambda x: x['avg_rating'] * x['num_ratings']**0.5)
            [lambda df: df["genres"].str.contains(genres, regex=True)]
            .loc[lambda df : ((df['year'] >= time_range[0]) & ( df['year'] <= time_range[1]))]
            .sort_values('combined_rating', ascending=False)
            .head(n)
            [['title', 'avg_rating', 'genres']]
            .rename(columns= {'title': 'Movie Title', 'avg_rating': 'Average Rating', 'genres': 'Genres'})
    )
    return recommendations

def get_popular_recommendations_streaming(n, genres, time_range, country, url, headers):
    recommendations = (
        ratings
            .groupby('movieId')
            .agg(avg_rating = ('rating', 'mean'), num_ratings = ('rating', 'count'))
            .merge(movies, on='movieId')
            .assign(combined_rating = lambda x: x['avg_rating'] * x['num_ratings']**0.5)
            [lambda df: df["genres"].str.contains(genres, regex=True)]
            .loc[lambda df : ((df['year'] >= time_range[0]) & ( df['year'] <= time_range[1]))]
            .sort_values('combined_rating', ascending=False)
            .head(n)
            [['title', 'avg_rating', 'genres', 'movieId']]
    )
    # merge recommendations with links df to get imdbIds for the API calls
    recommendations_ids =   (
                            recommendations
                                .merge(links, how = 'left', on = 'movieId')
                                # [['title', 'genres', 'imdbId']]
                            )
    recommendations_ids['imdbId'] = 'tt0' + recommendations_ids['imdbId'].astype('str')
    imdb_ids = list(recommendations_ids['imdbId'])

    # create new column for streaming links
    recommendations_ids['Streaming Availability'] = ""

    # loop through imdb_ids to make one api call for each to get available streaming links
    for id in imdb_ids:

        # make api call
        querystring = {"country":country,"imdb_id":id,"output_language":"en"}
        response = requests.request("GET", url, headers=headers, params=querystring)
        streaming_info = response.json()

        for streaming_service in streaming_info['streamingInfo']:
            recommendations_ids.loc[recommendations_ids['imdbId'] == id, 'Streaming Availability'] += f"{streaming_service}: {streaming_info['streamingInfo'][streaming_service][country]['link']} \n" 

    recommendations_ids.rename(columns= {'title': 'Movie Title', 'genres': 'Genres'}, inplace = True)

    return recommendations_ids[['Movie Title', 'Genres', 'Streaming Availability']]

def transform_genre_to_regex(genres):
    regex = ""
    for genre in genres:
        regex += f"(?=.*{genre})"
    return regex

# USER INPUT:

st.write("""
Move the slider to the desired number of recommendations you wish to receive.  
""")
number_of_recommendations = st.slider("Number of recommendations", 1, 10, 5)

st.write("""
Move the sliders to choose a timeperiod for your recommendations.
""")
time_range = st.slider('Time-period:', min_value=1900, max_value=2018, value=(1900, 2018), step=1)

st.write("""
__Optional__: You can narrow down the recommendations by picking one or several genre(s).  
However, the more genres you choose, the fewer movies will be recommended.
""")
genre_list = set([inner for outer in movies.genres.str.split('|') for inner in outer])
genres = st.multiselect('Optional: Select one or more genres', genre_list, default=None, key=None, help=None, on_change=None, args=None, kwargs=None, disabled=False)
genres_regex = transform_genre_to_regex(genres)

st.write("""
__Optional__: You can receive links for popular streaming services for each  recommendation (if available) by selecting your countrycode.  
Select none if you don't want to get streaming links.  
""")
streaming_country = st.selectbox('Optional: Country for streaming information', ('none', 'de', 'us'))

# API INFORMATION:
# Streaming availability
url = "https://streaming-availability.p.rapidapi.com/get/basic"
headers = {
	"X-RapidAPI-Key": api_keys.streaming_api_key,
	"X-RapidAPI-Host": "streaming-availability.p.rapidapi.com"
}

# EXECUTION:

if st.button("Get Recommendations"):
    if streaming_country == 'none':
        st.write(get_popular_recommendations(number_of_recommendations, genres_regex, time_range))
    else: 
        try:
            recommendations = get_popular_recommendations_streaming(number_of_recommendations, genres_regex, time_range, streaming_country, url, headers)
            st.write("Double-click on a Streaming-Availability cell to see all options.", recommendations)
        except:
            recommendations = get_popular_recommendations(number_of_recommendations, genres_regex, time_range)
            st.write('Error: Streaming information could not be gathered. Providing output without streaming availability instead.', recommendations)