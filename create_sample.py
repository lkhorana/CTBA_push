import pandas as pd

# Load the full dataset (if it's outside CTBA_push, use the absolute path)
full_df = pd.read_csv("CTBA_push/data/glassdoor.csv")  # or provide full path

# Take a smaller sample
sample_df = full_df.sample(n=5000, random_state=42)  # 5000 rows for testing

# Save the sample
sample_df.to_csv("CTBA_push/data/glassdoor.csv", index=False)

print("Sample CSV created successfully!")
