import os
import pandas as pd

# Get the current directory where your Python script is located
script_dir = os.path.dirname(__file__)

# Create an empty DataFrame to store the merged data
merged_data = pd.DataFrame()

# Loop through all files in the directory
for filename in os.listdir(script_dir):
    if filename.endswith('.xlsx'):
        # Load each Excel file into a DataFrame
        file_path = os.path.join(script_dir, filename)
        df = pd.read_excel(file_path)
        
        # Concatenate the data from the current file to the merged_data DataFrame
        merged_data = pd.concat([merged_data, df], ignore_index=True)

# Save the merged data to a new Excel file
merged_data.to_excel('merged_data.xlsx', index=False)

print("Merged data saved as 'merged_data.xlsx'")
