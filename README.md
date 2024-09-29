# Company Research and PDF Report Generator

This project is designed to automate the process of researching companies through web scraping and generating PDF reports based on predefined questions. It leverages the **OpenAI API** to extract insights from scraped data and uses **Poetry** for dependency management.

## Project Structure

```bash
WEB_SCRAPING_OPENAI/
│
├── Generated_Reports/          # Folder where final PDF reports are stored
├── Generated_Website_CSV/      # Folder where updated CSV files are saved
├── openai_responses/           # Folder storing OpenAI API JSON responses
├── scraped_websites/           # Folder containing scraped website text files
│
├── 0_start_scrape_JSON.py      # Main script that initiates the scraping process
├── 1_Create_Many_Reports.py    # Script to convert JSON responses into formatted PDFs
├── 2_OAIS_JSON.py              # Script to scrape websites and save text files
├── 3_web_scraper_multithreaded.py  # Script to query OpenAI API with scraped text
│
├── input_websites.csv          # CSV file containing the list of websites to scrape
│
├── poetry.lock                 # Poetry lock file for dependency management
├── pyproject.toml              # Project configuration file for Poetry
```
## How It Works

1. **Initial Setup**
   - The user provides a list of websites in `input_websites.csv`.
   - The main script, `0_start_scrape_JSON.py`, orchestrates the entire process by running the scripts `2_OAIS_JSON.py` and `3_web_scraper_multithreaded.py` iteratively for each website.

2. **Web Scraping**
   - The script `2_OAIS_JSON.py` scrapes each website listed in `input_websites.csv` and saves the generated text file in the `scraped_websites/` folder.

3. **OpenAI Querying**
   - The scraped text is passed to the OpenAI API through `3_web_scraper_multithreaded.py`, where predefined questions are set. The API responses are saved in the `openai_responses/` folder as JSON files.

4. **PDF Report Generation**
   - The script `1_Create_Many_Reports.py` processes all the JSON files in `openai_responses/` and converts them into easily readable PDF reports, which are saved in the `Generated_Reports/` folder.
   - This script also updates the corresponding CSV files as it processes the reports.

## Setup Instructions

1. **Install Dependencies**
   Ensure you have **Poetry** installed for dependency management. Run the following command to install the project dependencies:

```bash
   poetry install
```

### 2. Running the Project
To start the entire process, run the `0_start_scrape_JSON.py` script:

```bash
   python 0_start_scrape_JSON.py
```

This will automatically scrape the websites, query OpenAI for insights, and generate PDF reports.

### 3. Customizing Queries
The queries sent to OpenAI can be customized in `3_web_scraper_multithreaded.py` based on the specific information you want to extract from the scraped text.

## Dependencies

- **Python 3.x**
- **Poetry** for dependency management
- **OpenAI API key** (required for querying OpenAI)

## Future Improvements

- Adding error handling for failed website scrapes.
- Enhancing the PDF formatting for more detailed reporting.
- Optimising the multithreaded scraping process for faster performance.



