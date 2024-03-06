import pandas as pd
import glob

# Path to the directory containing CSV files
directory_path = "data/CourseReport"

# Get a list of all CSV files in the directory
csv_files = glob.glob(directory_path + "/*.csv")

# Initialize an empty list to store DataFrames
dfs = []

# Iterate over each CSV file
for csv_file in csv_files:
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file, sep=";")
    # Append the DataFrame to the list
    dfs.append(df)

# Concatenate all DataFrames in the list along rows
result_df = pd.concat(dfs, ignore_index=True)

# Save the concatenated DataFrame to a new CSV file
result_df.to_csv("data/CourseReport/combined_data.csv", index=False, sep=";")
