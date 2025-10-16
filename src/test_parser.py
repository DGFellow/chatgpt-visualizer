from data_parser import load_conversations
df = load_conversations('data/conversations.json')
print(df.head())  # Check first few rows
print("\nSample thread:\n", df.iloc[0]['thread'])