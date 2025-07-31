import streamlit as st
import requests

API_URL = "http://127.0.0.1:5000/predict"

st.title("Clickbait vs Substance Detector")

headline = st.text_input("Enter News Headline:")
article = st.text_area("Enter Full Article:")

if st.button("Predict"):
    if not headline.strip() or not article.strip():
        st.warning("Please provide both headline and article.")
    else:
        payload = {"headline": headline, "article": article}
        try:
            response = requests.post(API_URL, json=payload)
            if response.status_code == 200:
                result = response.json()
                label = result["prediction"]
                score = result["headline_score"]
                st.success(f"Prediction: **{label}**")
                st.info(f"Headline score: {score:.2f}")
            else:
                st.error(f"API error: {response.text}")
        except Exception as e:
            st.error(f"Failed to connect to API: {e}")
