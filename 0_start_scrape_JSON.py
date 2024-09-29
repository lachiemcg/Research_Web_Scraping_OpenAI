import csv
import subprocess
import os
import pandas as pd
from datetime import datetime
import re
import json


# Function to run the OpenAI analysis
def run_analysis(url):
    # Run the open_ai_scrape.py script with the provided URL
    subprocess.run(["python", "2_OAIS_JSON.py", url])

# Function to update the CSV file with answers
def update_csv(csv_file):
    df = pd.read_csv(csv_file)

    for index, row in df.iterrows():
        url = row['website']

        # Run the analysis for the given URL
        run_analysis(url)

        # Determine the generated filename and filepath
        webpage_name = re.sub(r'[^a-zA-Z0-9]', '_', url.split("//")[-1].split('/')[0])  # Extract the domain name
        timestamp = datetime.now().strftime('%Y%m%d_%H')  # Date and hour only
        response_filename = f"openairesponse_{webpage_name}_{timestamp}.json"
        response_filepath = os.path.join("openai_responses", response_filename)

        # Read the OpenAI response JSON file
        try:
            with open(response_filepath, "r", encoding="utf-8") as file:
                response_data = json.load(file)
                print(f"Found and read response file: {response_filepath}")
        except FileNotFoundError:
            print(f"Response file not found: {response_filepath}")
            continue

        # Update the DataFrame with the answers
        df.at[index, 'overview'] = response_data.get('overview', '')
        df.at[index, 'housing_provider'] = response_data.get('housing_provider', '')
        df.at[index, 'housing_services'] = response_data.get('housing_services', '')
        df.at[index, 'case_management'] = response_data.get('case_management', '')
        df.at[index, 'case_management_duration'] = response_data.get('case_management_duration', '')
        df.at[index, 'wrap_around_support'] = response_data.get('wrap_around_support', '')
        df.at[index, 'key_partners'] = response_data.get('key_partners', '')
        df.at[index, 'financial_supporters'] = response_data.get('financial_supporters', '')

        # Debugging: Print the updated DataFrame row
        print(f"Updated row {index}: {df.iloc[index]}")

    # Save the updated DataFrame back to the same CSV file
    df.to_csv(csv_file, index=False)
    print(f"CSV file updated and saved: {csv_file}")

# Start the process and update the input CSV file
update_csv('input_websites.csv')
