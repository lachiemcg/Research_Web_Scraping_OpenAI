import subprocess
import os
from datetime import datetime
import openai
import re
import json
import sys

# Get the start_url from command-line arguments
if len(sys.argv) < 2:
    print("Usage: python open_ai_scrape.py <start_url>")
    sys.exit(1)

start_url = sys.argv[1]

# Step 1: Run the web scraper script with the provided start_url
subprocess.run(["python", "3_web_scraper_multithreaded.py", start_url])

# Step 2: Determine the generated filename and filepath
webpage_name = re.sub(r'[^a-zA-Z0-9]', '_', start_url.split("//")[-1].split('/')[0])  # Extract the domain name
timestamp = datetime.now().strftime('%Y%m%d_%H')  # Date and hour only
filename = f"{webpage_name}_{timestamp}.txt"
filepath = os.path.join("scraped_websites", filename)  # Use the correct folder path

# Step 3: Read the generated text file
try:
    with open(filepath, "r", encoding="utf-8") as file:
        scraped_content = file.read()
except UnicodeDecodeError:
    # If UTF-8 fails, try with a more permissive encoding like 'latin-1' or 'iso-8859-1'
    with open(filepath, "r", encoding="iso-8859-1") as file:
        scraped_content = file.read()

# Step 4: Prepare the query and send it to the OpenAI API
query = f"""
Please analyze the provided text file and answer the following questions in a detailed and comprehensive manner. Ensure the response is as long and informative as possible, embedding direct weblinks to specific pages within the organization’s website where relevant information is referenced. Be explicit about names, program details, and partnerships. Avoid using markdown syntax like asterisks (**) except please clearly mark the beginning of your answer to each question with "### Answer {{number}} ###".Please embed the links naturally within the text.

0. Provide an overview of this organization, including its history, mission, and key areas of focus. Discuss the significance of its work in the community and any unique aspects that distinguish it from other organizations.
   
1. Confirm whether this organization functions as a housing provider. If so, discuss how housing fits into their broader mission and the importance of housing within their service offerings.
   
2. Describe in detail the types of housing services they provide (e.g., temporary, crisis, long-term). For each type of housing, explain the specific programs they offer, the target demographic, and any available statistics or outcomes associated with these programs.

3. Investigate whether they offer case management support as part of their services. If they do, detail the scope of this support, the specific programs that include case management, and the qualifications or roles of the staff providing this support.

4. If case management is provided, clarify whether it is ongoing or time-limited. Provide examples of how ongoing support is delivered and its impact on clients’ long-term stability.

5. Outline other forms of wrap-around support they offer in addition to housing and case management. Describe how these services complement their housing programs and contribute to overall client well-being. Include any partnerships or collaborations with other organizations that enhance these services.

6. Identify their key partners across government, charity, and corporate sectors. Provide details on how these partnerships function, the contributions each partner makes, and how these partnerships align with the organization’s mission.

7. Discuss whether the organization talks about its financial supporters. If they do, describe how they acknowledge these supporters, the impact of financial contributions on their programs, and any specific examples of campaigns or donor recognition efforts mentioned in the text.

--- Begin Text ---
{scraped_content}
--- End Text ---
"""

# Initialize the OpenAI API client with your API key
openai.api_key = "add_your_own_api_here"

# Send the request to the OpenAI API
completion = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": query}
    ]
)

# Extract the content from the response
response_text = completion.choices[0].message.content

# Split the response into answers
answers = re.split(r'### Answer \d+ ###', response_text.strip())[1:]

# Map the answers to a JSON structure
response_data = {
    "overview": answers[0].strip() if len(answers) > 0 else "",
    "housing_provider": answers[1].strip() if len(answers) > 1 else "",
    "housing_services": answers[2].strip() if len(answers) > 2 else "",
    "case_management": answers[3].strip() if len(answers) > 3 else "",
    "case_management_duration": answers[4].strip() if len(answers) > 4 else "",
    "wrap_around_support": answers[5].strip() if len(answers) > 5 else "",
    "key_partners": answers[6].strip() if len(answers) > 6 else "",
    "financial_supporters": answers[7].strip() if len(answers) > 7 else ""
}

# Step 5: Prepare the subfolder and unique filename
output_dir = "openai_responses"
os.makedirs(output_dir, exist_ok=True)  # Create the subfolder if it doesn't exist

# Generate a unique filename for JSON output
output_filename = f"openairesponse_{webpage_name}_{timestamp}.json"
output_filepath = os.path.join(output_dir, output_filename)

# Step 6: Save the response to the JSON file in the subfolder
with open(output_filepath, "w", encoding="utf-8") as output_file:
    json.dump(response_data, output_file, indent=4)

print(f"Response saved to {output_filepath}")
