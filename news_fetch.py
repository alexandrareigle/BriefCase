from newsapi import NewsApiClient
from dotenv import load_dotenv
import os

#Loading API key from .env file
load_dotenv()
api_key=os.getenv("NEWS_API_KEY")

#Connect to NewsAPI
newsapi=NewsApiClient(api_key=api_key)

def get_news(topic):
    articles=newsapi.get_everything(
        q=topic,
        language="en",
        sort_by="publishedAt",
        page_size=3  #top 3 articles
    )

    print(f"\n=== News for: {topic} ===")
    for articles in articles["articles"]:
        print(f"Headline: {articles['title']}")
        print(f"Source: {articles['source']['name']}")
        print(f"Link: {articles['url']}")
        print("---")

#TESTING
get_news("Federal Reserve")