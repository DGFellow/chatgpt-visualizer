from data_parser import load_conversations
import pandas as pd

# Load the data
df = load_conversations('data/conversations.json')

# Show only the first 5 rows with selected columns for clarity
print("First 5 rows of the DataFrame:")
print(df[['title', 'display_title', 'create_time']].head().to_string())

# Check if 'display_title' exists and print a sample
if 'display_title' in df.columns:
    print("\nSample 'display_title' values:")
    print(df['display_title'].head().tolist())
else:
    print("\n'display_title' column not found!")