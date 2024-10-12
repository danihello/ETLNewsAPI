import requests
from etl_project.assets.utils import get_yesterday

class NewsApiClient:
    """
    Provides a client for interacting with the News API to retrieve news articles.

    The `NewsApiClient` class is responsible for making requests to the News API and returning news article data. It supports retrieving news articles based on a search query, language, and date range, as well as retrieving top headlines based on country and/or category.

    The class requires an API key to be provided during initialization, which is used to authenticate the requests to the News API.
    """

    def __init__(self, api_key: str):
        if api_key is None:
            raise Exception("API Key cannot be set to None")
        self.api_key = api_key
        self.base_url="https://newsapi.org/v2"

    def get_news(self, query, language:str='en', from_date=None, to_date=None, pageSize:int=100) -> list:
        """
        Retrieves news articles based on the provided search query, language, and date range.
        
        Args:
            query (str): The search query to use for retrieving news articles.
            language (str, optional): The language of the news articles to retrieve. Defaults to 'en'.
            from_date (str, optional): The start date for the news articles, in the format 'YYYY-MM-DD'. Defaults to yesterday's date.
            to_date (str, optional): The end date for the news articles, in the format 'YYYY-MM-DD'. Defaults to yesterday's date.
            pageSize (int, optional): The maximum number of news articles to retrieve. Defaults to 100.
        
        Returns:
            list: A list of news article dictionaries, containing information such as the title, description, and URL.
        """
        yesterday = get_yesterday().isoformat()
        if from_date is None:
            from_date = yesterday
        if to_date is None:
            to_date = yesterday
        url = f'{self.base_url}/everything'
        params = {
            'q': query,
            'language': language,
            'from': from_date,
            'to':to_date
        }
        headers = {
            'X-Api-Key': api_key
        }
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            news_data = response.json()
            return news_data['articles']
        else:
            print(f"Error: {response.status_code}")
            return []
    
    def get_top_headlines(self, country=None, category=None) -> list:
        """
        Retrieves the top news headlines based on the provided country and/or category.
        
        Args:
            country (str, optional): The country code to filter the top headlines by. Defaults to 'us'.
            category (str, optional): The news category to filter the top headlines by.
        
        Returns:
            list: A list of news article dictionaries, containing information such as the title, description, and URL.
        """
        if country is None:
            country = 'us'
        url = f'{self.base_url}/top-headlines'
        params = {
            'country': country,
            'category': category
        }
        headers = {
            'X-Api-Key': api_key
        }
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            news_data = response.json()
            return news_data['articles']
        else:
            print(f"Error: {response.status_code}")
            return []
api_key='58c2489477ef49a6bb9dca4e5c7932c6'