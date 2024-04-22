import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os

def save_errors_to_file(error_list, folder):
    """Save the list of error URLs to a file in the specified folder."""
    error_filename = os.path.join(folder, "ERRORS.txt")
    with open(error_filename, 'w', encoding='utf-8') as file:
        for url in error_list:
            file.write(url + '\n')
    print(f"Errors logged in '{error_filename}'")

def fetch_text_and_save(url, folder, error_list):
    """Fetch the text content from a URL and save it to a file in the specified folder."""
    # Create a filename based on the URL
    filename = url.replace("://", "_").replace("/", "_").replace("?", "_").replace(":", "_") + ".txt"
    filepath = os.path.join(folder, filename)
    
    try:
        # Fetch the web page content using requests
        response = requests.get(url)
        
        # Check if the request was successful (status code 200)
        if response.status_code != 200:
            print(f"Failed to fetch the web page at URL '{url}'. Status code: {response.status_code}")
            # Add the error URL to the list of errors
            error_list.append(url)
            return False
        
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract the text from the parsed HTML
        text = soup.get_text()
        
        # Save the text to the specified file in the folder
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(text)
        
        print(f"Successfully saved content from '{url}' to '{filepath}'")
        return True
    
    except Exception as e:
        # Handle any errors that occur during the fetching or saving process
        print(f"An error occurred while processing URL '{url}': {e}")
        # Add the error URL to the list of errors
        error_list.append(url)
        return False

def find_and_save_sub_urls(main_url, error_list):
    """Find all sub-URLs in a main URL, save their text content to files, and log any errors."""
    # Create a folder for the main URL based on its domain name
    parsed_url = urlparse(main_url)
    folder_name = parsed_url.netloc.replace("www.", "")
    folder = os.path.join(os.getcwd(), folder_name)
    os.makedirs(folder, exist_ok=True)

    # Save the main URL text content to a file in the folder
    fetch_text_and_save(main_url, folder, error_list)
    
    # Fetch the main page content using requests
    try:
        response = requests.get(main_url)
        
        # Check if the request was successful (status code 200)
        if response.status_code != 200:
            print(f"Failed to fetch the main web page at URL '{main_url}'. Status code: {response.status_code}")
            error_list.append(main_url)
            return
        
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all anchor tags (<a>) with href attribute
        links = soup.find_all('a', href=True)
        
        # Initialize a set to store unique sub-URLs
        sub_urls = set()

        # Loop through all found links
        for link in links:
            # Get the href attribute (URL) of the anchor tag
            href = link['href']
            
            # Skip mailto links
            if href.startswith('mailto:'):
                continue
            
            # Join the URL with the main URL to handle relative links
            full_url = urljoin(main_url, href)
            
            # Add the full URL to the set of sub-URLs
            sub_urls.add(full_url)
        
        # Loop through the set of sub-URLs and save each to a text file in the folder
        for url in sub_urls:
            fetch_text_and_save(url, folder, error_list)

    except Exception as e:
        # Handle any errors that occur during the fetching or parsing process
        print(f"An error occurred while processing the main URL '{main_url}': {e}")
        error_list.append(main_url)

def main():
    while True:
        # Get the main URL from the user
        main_url = input("Enter the main URL of the website (or 'exit' to quit): ")
        
        if main_url.lower() == 'exit':
            print("Exiting the program.")
            break
        
        # Initialize a list to store errors
        error_list = []
        
        # Call the function to find and save sub-URLs and their text content
        find_and_save_sub_urls(main_url, error_list)
        
        # If there were errors, save them to a file in the corresponding folder
        if error_list:
            # Create a folder for the main URL based on its domain name
            parsed_url = urlparse(main_url)
            folder_name = parsed_url.netloc.replace("www.", "")
            folder = os.path.join(os.getcwd(), folder_name)
            # Save the list of errors to a text file in the folder
            save_errors_to_file(error_list, folder)

if __name__ == "__main__":
    main()
