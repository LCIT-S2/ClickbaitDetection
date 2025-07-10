
import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from pymongo import MongoClient

# Replace with your actual MongoDB Atlas URI
MONGO_URI = "mongodb+srv://preetsoniiii19:123456Pk@clickbaitcluster.rinh1jn.mongodb.net/?retryWrites=true&w=majority&appName=Clickbaitcluster"
client = MongoClient(MONGO_URI)
db = client["news_db"]
collection = db["articles"]

# Example Scraper (CNN only here for brevity)
def scrape_cnn():
    base_url = "https://edition.cnn.com"
    urls = [base_url, f"{base_url}/world", f"{base_url}/politics", f"{base_url}/entertainment"]
    results = []
    for url in urls:
        try:
            r = requests.get(url, timeout=10)
            soup = BeautifulSoup(r.content, 'html.parser')
            links = soup.find_all("a", href=True)
            for link in links:
                href = link.get("href")
                if href.startswith("/") and "/videos/" not in href:
                    article_url = base_url + href
                    headline = link.get_text(strip=True)
                    if not headline:
                        continue
                    try:
                        article_r = requests.get(article_url, timeout=10)
                        article_soup = BeautifulSoup(article_r.content, 'html.parser')
                        paragraphs = article_soup.find_all("div", class_="paragraph") or article_soup.find_all("p")
                        article_text = " ".join(p.get_text(strip=True) for p in paragraphs)
                        author_tag = article_soup.find("span", class_="metadata__byline__author")
                        publish_date_tag = article_soup.find("meta", {"itemprop": "datePublished"})
                        results.append({
                            "headline": headline,
                            "article": article_text,
                            "author": author_tag.get_text(strip=True) if author_tag else None,
                            "publish_date": publish_date_tag['content'] if publish_date_tag else None,
                            "source": "CNN",
                            "url": article_url,
                            "timestamp": datetime.now()
                        })
                    except:
                        continue
        except:
            continue
    return results

# Streamlit UI
st.title("Live News Scraper Dashboard")

if st.button("Scrape News Now"):
    with st.spinner("Scraping in progress..."):
        df = pd.DataFrame(scrape_cnn())
        if not df.empty:
            records = df.to_dict(orient="records")
            collection.insert_many(records)
            st.success(f"{len(df)} articles scraped and stored in MongoDB Atlas.")
            st.dataframe(df[["headline", "author", "publish_date", "source", "url"]])
        else:
            st.error("No articles were scraped. Please try again.")
