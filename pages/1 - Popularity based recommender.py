import streamlit as st

st.title("Test Page")
 
st.write("""
### Instructions
Check the Sidebar and choose a recommender that suits your purpose.  
""")

if st.button("TEST"):

    st.write(movies.head(10))