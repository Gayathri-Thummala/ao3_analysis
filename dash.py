import streamlit as st
import pandas as pd
import numpy as np
import joblib
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import MultiLabelBinarizer

# Load the CSV file (replace with your actual file path if necessary)
df = pd.read_csv('queen_of_tears_ao3_data.csv')

# Load the saved MultiLabelBinarizer (tags encoder)
mlb = joblib.load('mlb_encoder_rf.pkl')  # MultiLabelBinarizer for tags

# Title and Introduction
st.title('Queen of Tears Fanfiction Analysis')
st.markdown("""
This dashboard provides an interactive analysis of the **Queen of Tears** fanfiction data.
Explore trends related to **kudos**, **comments**, **word count**, and **tags**.
""")

# Sidebar: User input for tags (multiple tags allowed)
tags_input = st.sidebar.text_input('Enter Tags (comma separated)', '')

# Convert tags input into a list
tags_list = tags_input.split(', ') if tags_input else []

# One-hot encode the tags input using the MultiLabelBinarizer
tags_encoded_input = mlb.transform([tags_list])

# Sidebar: Slider to choose the number of top works to display
num_top_works = st.sidebar.slider('Number of Top Works to Display:', 1, 20, 5)

# Sidebar: Dropdown to select a specific tag
selected_tag = st.sidebar.selectbox('Choose a Tag', df['tags'].str.split(', ').explode().unique())


# Function to recommend fanfictions based on tags
def recommend_fanfictions(tags_list):
    if not tags_list:
        st.write("Please enter some tags.")
        return

    # Ensure tags are strings and handle NaN values in 'tags' column
    df['tags'] = df['tags'].fillna('')  # Fill NaN values with an empty string
    df['tags'] = df['tags'].astype(str)  # Ensure all values are strings

    # Filter fanfictions that contain the selected tags
    matched_fanfictions = df[df['tags'].apply(lambda x: all(tag in x for tag in tags_list))]

    if matched_fanfictions.empty:
        st.write("No exact matches found for the tags entered. Showing recommendations for individual tags.")

        # If no exact match, show fanfictions with any of the tags
        matched_fanfictions = df[df['tags'].apply(lambda x: any(tag in x for tag in tags_list))]

    # Sort the results by kudos (highest first) and display the top N (from slider)
    matched_fanfictions = matched_fanfictions.nlargest(num_top_works, 'kudos')

    # Show the recommended fanfictions
    st.subheader(f'Top {num_top_works} Recommended Fanfictions:')
    st.write(matched_fanfictions[['title', 'author', 'tags', 'kudos', 'word_count']])

    return matched_fanfictions


# Use Streamlit tabs for separate views
tab1, tab2 = st.tabs(["Recommendation System", "Analytics"])

with tab1:
    # Call the function to recommend fanfictions based on the tags entered by the user
    recommended_fanfictions = recommend_fanfictions(tags_list)

with tab2:
    # Display the analytics (Top N Fanfictions, Kudos Distribution, Word Count vs Kudos)
    st.subheader(f'Top {num_top_works} Fanfictions Based on Kudos')
    top_works = df.nlargest(num_top_works, 'kudos')
    st.write(top_works[['title', 'author', 'tags', 'kudos', 'word_count']])

    # Bar chart for kudos distribution
    st.subheader('Distribution of Kudos')
    st.bar_chart(df['kudos'])

    # Scatter plot for Word Count vs Kudos
    st.subheader('Word Count vs Kudos')
    fig, ax = plt.subplots()
    sns.scatterplot(x='word_count', y='kudos', data=df, ax=ax)
    ax.set_title('Word Count vs Kudos')
    ax.set_xlabel('Word Count')
    ax.set_ylabel('Kudos')
    st.pyplot(fig)

    # Filter the data by selected tag
    filtered_data = df[df['tags'].str.contains(selected_tag, na=False)]
    st.subheader(f'Works with the tag "{selected_tag}":')
    st.write(filtered_data[['title', 'author', 'tags', 'kudos']])
