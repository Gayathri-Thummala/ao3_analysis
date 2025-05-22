import pandas as pd

# Load the CSV file into a Pandas DataFrame
df = pd.read_csv('queen_of_tears_ao3_data.csv')

# Display the first few rows of the dataframe to understand its structure
print(df.head())

# Basic summary of the dataframe
print("\nSummary of Data:")
print(df.describe())

# Check for missing values
print("\nMissing values in each column:")
print(df.isnull().sum())

# Get the data types of each column
print("\nData types of each column:")
print(df.dtypes)

import seaborn as sns
import matplotlib.pyplot as plt

df['tags'] = df['tags'].fillna('')  # Replace NaN with an empty string
df['tags'] = df['tags'].astype(str)  # Ensure all values are strings

# Now, you can split the tags and repeat the kudos and hits
tags_exploded = df['tags'].str.split(', ').explode().reset_index(drop=True)
hits_exploded = df['hits'].repeat(df['tags'].str.split(', ').apply(len)).reset_index(drop=True)
kudos_exploded = df['kudos'].repeat(df['tags'].str.split(', ').apply(len)).reset_index(drop=True)

# Create a new DataFrame
tags_data = pd.DataFrame({
    'tag': tags_exploded,
    'hits': hits_exploded,
    'kudos': kudos_exploded
})

# Group by tag and calculate the mean kudos and hits
tag_analysis = tags_data.groupby('tag').agg({'kudos': 'mean', 'hits': 'mean'}).reset_index()

# Visualizing the results


# Top 10 tags by average kudos
top_tags = tag_analysis.nlargest(10, 'kudos')
top_tags.plot(kind='bar', x='tag', y='kudos', title='Top 10 Tags by Average Kudos')
plt.xlabel('Tag')
plt.ylabel('Average Kudos')
plt.show()

plt.figure(figsize=(10, 6))
sns.scatterplot(x='word_count', y='hits', data=df, alpha=0.6)
plt.title('Word Count vs Hits')
plt.xlabel('Word Count')
plt.ylabel('Hits')
plt.show()

# Calculate correlation between Word Count and Hits
correlation_wc_hits = df['word_count'].corr(df['hits'])
print(f"Correlation between Word Count and Hits: {correlation_wc_hits:.2f}")