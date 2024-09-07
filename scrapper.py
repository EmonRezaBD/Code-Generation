import requests
from bs4 import BeautifulSoup
import json

#url = "https://github.com/<username>/<repository>/commit/<commit_id>"
# GitHub URL for the commit
url = "https://github.com/emscripten-core/emscripten/commit/1d9f405ed57b31f3cd5a041c1b860ba73cc490df"

# Custom headers to avoid 406 error
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

# Function to scrape the commit diff from GitHub
def scrape_github_commit(url):
    # Send a GET request to fetch the page content with custom headers
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return None

    # Parse the page content using BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find all table rows ('tr') with the class 'blob-code'
    diff_elements = soup.find_all("td", class_="blob-code") #all elements of the webpage

    if not diff_elements:
        print("No code diff found on the page.")
        return None
    
    # Extract the changes
    changes = []
    for elem in diff_elements: 
        # Extract the line of code from the element
        line = elem.get_text().strip()
        changes.append(line)
    
    return changes

# Function to write code changes into a JSON Lines (.jsonl) file
def write_to_jsonl(file_name, changes):
    with open(file_name, 'w', encoding='utf-8') as f:
        for change in changes:
            # Create a dictionary for each change and dump it into JSON format
            json_line = json.dumps({"code": change}, ensure_ascii=False)
            f.write(json_line + '\n')

# Main function to run the scraper
def main():
    # Scrape the code changes from the GitHub commit page
    changes = scrape_github_commit(url)
    
    if changes:
        # Write the code changes to a JSONL file
        jsonl_file = "code_changes.jsonl"
        write_to_jsonl(jsonl_file, changes)
        print(f"Code changes have been written to {jsonl_file}")
    else:
        print("No changes were found.")

if __name__ == "__main__":
    main()
