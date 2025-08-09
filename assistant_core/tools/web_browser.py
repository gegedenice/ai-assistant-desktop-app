import requests
from bs4 import BeautifulSoup

class WebBrowserTool:
    def search(self, query: str) -> str:
        """
        Searches the web for a given query using DuckDuckGo, fetches the first result,
        and returns the text content of that page.
        """
        search_url = f"https://duckduckgo.com/html/?q={query}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }

        try:
            # Get the search results page
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()

            # Find the first result link
            soup = BeautifulSoup(response.text, 'html.parser')
            first_link = soup.find('a', class_='result__a')

            if not first_link or not first_link.get('href'):
                return "Could not find a relevant link for the search query."

            # Get the URL and fetch its content
            page_url = first_link.get('href')
            # The URL from DDG is a redirect, we need to handle it
            if page_url.startswith("/l/"):
                page_url = "https://duckduckgo.com" + page_url

            page_response = requests.get(page_url, headers=headers, timeout=10, allow_redirects=True)
            page_response.raise_for_status()

            # Extract and return the text
            page_soup = BeautifulSoup(page_response.text, 'html.parser')
            # Get text and limit the length to avoid overly long responses
            text_content = page_soup.get_text(separator=' ', strip=True)
            return text_content[:4000]

        except requests.exceptions.RequestException as e:
            return f"An error occurred while searching: {e}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"