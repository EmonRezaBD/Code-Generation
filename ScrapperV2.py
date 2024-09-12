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
    
    #Checking if Single function change
    find_function_name = soup.find("td", class_="blob-code-hunk")
    function_name = find_function_name.get_text(strip=True)

    if '(' in function_name and ')' in function_name: #Checking function signature 

        # Extract the commit title (the bold part in the title)
        commit_title_element = soup.find("div", class_="commit-title")
        commit_title = commit_title_element.get_text(strip=True) if commit_title_element else "No Title Found"

        #list for storing parsed code elements
        minus_version = []   # Codes with -
        plus_version = []   # Codes with +
        normal_version = []       # Codes without + and - lines
        before_commit_list = [] # Codes with - and normal_version
        after_commit_list = [] # Codes with + and normal_version
        

        minusCode = soup.find_all("td", class_="blob-code-deletion")
        plusCode = soup.find_all("td", class_="blob-code-addition")
        normalCode = soup.find_all("td", class_="blob-code-context")
        before_commit_code = soup.find_all(["td"], class_=["blob-code-deletion", "blob-code-context"])
        after_commit_code = soup.find_all(["td"], class_=["blob-code-addition", "blob-code-context"])


        for line in minusCode:
            code_line = line.get_text(strip=True)
            minus_version.append(code_line)

        for line in plusCode:
            code_line = line.get_text(strip=True)
            plus_version.append(code_line)
        
        for line in normalCode:
            code_line = line.get_text(strip=True)
            normal_version.append(code_line)
        
        for line in before_commit_code:
            code_line = line.get_text(strip=True)
            before_commit_list.append(code_line)

        for line in after_commit_code:
            code_line = line.get_text(strip=True)
            after_commit_list.append(code_line)

        # Join the lists into strings
        only_addition_codes = "\n".join(plus_version)   
        only_deletion_codes = "\n".join(minus_version)   
        normal_codes = "\n".join(normal_version)   
        before_commit_codes = "\n".join(before_commit_list)   
        after_commit_codes = "\n".join(after_commit_list)   
            

        # Return a dictionary with the commit title and the categorized code blocks
        return {
            "commit_title": commit_title,
            "commit_url": url,
            "only_addition_codes": only_addition_codes, 
            "only_deletion_codes": only_deletion_codes,
            "codes_without_addition_and_deletion": normal_codes,   
            "before_commit_codebase": before_commit_codes,       
            "after_commit_codebase":after_commit_codes       
        }

# Function to write commit data into a JSON Lines (.jsonl) file
def write_to_jsonl(file_name, commit_data):
    with open(file_name, 'a', encoding='utf-8') as f:  # 'a' for append
        # Format the commit as per your required output format
        formatted_data = {
            "Commit title": commit_data["commit_title"],
            "Commit url": commit_data["commit_url"],
            "Only_addition_codes": commit_data["only_addition_codes"],  
            "Only_deletion_codes": commit_data["only_deletion_codes"],    
            "Codes_without_addition_and_deletion": commit_data["codes_without_addition_and_deletion"],            
            "Before_commit_codebase": commit_data["before_commit_codebase"],        
            "After_commit_codebase": commit_data["after_commit_codebase"]        
        }
        json_line = json.dumps(formatted_data, ensure_ascii=False)
        f.write(json_line + '\n')

# Main function to run the scraper for each commit URL from the CSV
def main():
    # Read the CSV file and specify only the 'commit_url' column
    csv_file = 'E:\\Code-Generation\\Data_1func_changed.csv'  # Replace with your CSV file name
    df = pd.read_csv(csv_file, usecols=['commit_url'])  # Read only the commit_url column

    # Loop through each row in the CSV
    for index, row in df.iterrows():
        commit_urls = row['commit_url']

        # Split the commit_url field to handle multiple URLs, and select the first one
        first_commit_url = commit_urls.split(',')[0]  # Split on spaces and take the first URL
        
        print(f"Processing commit: {first_commit_url}")
        
        commit_data = scrape_github_commit(first_commit_url)
        
        if commit_data:
            # Write the commit title and body to a JSONL file
            jsonl_file = "DatasetWithCommitURL.jsonl"
            write_to_jsonl(jsonl_file, commit_data)
            print(f"Commit data has been written to {jsonl_file}")
        else:
            print(f"No data found for {first_commit_url}")

if __name__ == "__main__":
    main()
