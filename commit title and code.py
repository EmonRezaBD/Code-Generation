import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

# Custom headers to avoid 406 error
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

# Function to scrape the commit title and the full code from GitHub
def scrape_github_commit(url):
    # Send a GET request to fetch the page content with custom headers
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return None

    # Parse the page content using BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Extract the commit title (the bold part in the title)
    commit_title_element = soup.find("div", class_="commit-title")
    commit_title = commit_title_element.get_text(strip=True) if commit_title_element else "No Title Found"

    # Find all the table rows that contain the actual code
    diff_elements = soup.find_all("td", class_="blob-code")

    # Extract and join all the code lines
    commit_body_lines = [line.get_text(strip=True) for line in diff_elements]
    commit_body_text = "\n".join(commit_body_lines)

    # Return a dictionary with the commit title and body (full C++ code)
    return {
        "commit_title": commit_title,
        "commit_body": commit_body_text
    }

# Function to write commit title and body into a JSON Lines (.jsonl) file
def write_to_jsonl(file_name, commit_data):
    with open(file_name, 'a', encoding='utf-8') as f:  # 'a' for append
        # Format the commit as per your required output format
        formatted_data = {
            "Commit title": commit_data["commit_title"],
            "Commit body": commit_data["commit_body"]
        }
        json_line = json.dumps(formatted_data, ensure_ascii=False)
        f.write(json_line + '\n')

# Main function to run the scraper for each commit URL from the CSV
def main():
    # Read the CSV file and specify only the 'commit_url' column
    csv_file = 'E:\\Code-Generation\\issues.csv'  # Replace with your CSV file name
    df = pd.read_csv(csv_file, usecols=['commit_url'])  # Read only the commit_url column

    # Loop through each row in the CSV
    for index, row in df.iterrows():
        commit_urls = row['commit_url']

        # Split the commit_url field to handle multiple URLs, and select the first one
        first_commit_url = commit_urls.split(',')[0]  # Split on spaces and take the first URL
        
        print(f"Processing commit: {first_commit_url}")
        
        # Scrape the commit title and body (full code) from the GitHub commit page
        commit_data = scrape_github_commit(first_commit_url)
        
        if commit_data:
            # Write the commit title and body to a JSONL file
            jsonl_file = "commit_metadata.jsonl"
            write_to_jsonl(jsonl_file, commit_data)
            print(f"Commit data has been written to {jsonl_file}")
        else:
            print(f"No data found for {first_commit_url}")

if __name__ == "__main__":
    main()
