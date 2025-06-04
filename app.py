
import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import joblib
from textblob import TextBlob

# ----------------- SCRAPERS -----------------
def scrape_cnn():
    urls = [
        "https://edition.cnn.com",
        "https://edition.cnn.com/world",
        "https://edition.cnn.com/politics",
        "https://edition.cnn.com/entertainment"
    ]
    results = []
    for url in urls:
        try:
            r = requests.get(url, timeout=10)
            soup = BeautifulSoup(r.content, 'html.parser')
            headlines = [h.get_text(strip=True) for h in soup.find_all("span", class_="container__headline-text")]
            results += [{"headline": h, "source": "CNN", "timestamp": datetime.now()} for h in headlines]
        except Exception as e:
            print(f"Error scraping CNN {url}: {e}")
    return results

def scrape_bbc():
    urls = [
        "https://www.bbc.com/news",
        "https://www.bbc.com/news/world",
        "https://www.bbc.com/news/business",
        "https://www.bbc.com/news/technology"
    ]
    results = []
    for url in urls:
        try:
            r = requests.get(url, timeout=10)
            soup = BeautifulSoup(r.content, 'html.parser')
            headlines = [h.get_text(strip=True) for h in soup.find_all("span", class_="gs-c-promo-heading__title")]
            results += [{"headline": h, "source": "BBC", "timestamp": datetime.now()} for h in headlines]
        except Exception as e:
            print(f"Error scraping BBC {url}: {e}")
    return results

def scrape_buzzfeed():
    urls = [
        "https://www.buzzfeed.com",
        "https://www.buzzfeed.com/world",
        "https://www.buzzfeed.com/news"
    ]
    results = []
    for url in urls:
        try:
            r = requests.get(url, timeout=10)
            soup = BeautifulSoup(r.content, 'html.parser')
            headlines = [h.get_text(strip=True) for h in soup.find_all("h2") if "title" in "".join(h.get("class", []))]
            results += [{"headline": h, "source": "BuzzFeed", "timestamp": datetime.now()} for h in headlines]
        except Exception as e:
            print(f"Error scraping BuzzFeed {url}: {e}")
    return results

def live_scrape():
    return pd.DataFrame(scrape_cnn() + scrape_bbc() + scrape_buzzfeed())

# ----------------- MODEL PREDICTION -----------------
def classify_clickbait(headlines):
    try:
        model = joblib.load("clickbait_model.joblib")
        vectorizer = joblib.load("vectorizer.joblib")
        features = vectorizer.transform(headlines)
        predictions = model.predict(features)
        return predictions
    except:
        return ["Unknown"] * len(headlines)

def analyze_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        return "Positive"
    elif polarity < -0.1:
        return "Negative"
    return "Neutral"

# ----------------- STREAMLIT UI -----------------
st.title("📰 Clickbait vs Substance Detector (Live Headlines)")

if st.button("🔄 Scrape Headlines Now"):
    with st.spinner("Scraping headlines..."):
        df = live_scrape()
        if not df.empty:
            df['Clickbait'] = classify_clickbait(df['headline'])
            df['Sentiment'] = df['headline'].apply(analyze_sentiment)
    if df.empty:
        st.warning("⚠️ No headlines found.")
    else:
        st.success(f"✅ Scraped {len(df)} headlines")
        st.dataframe(df)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", data=csv, file_name="live_headlines.csv", mime="text/csv")
