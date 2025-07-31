from flask import Flask, request, jsonify
import joblib
import re
from nltk.stem import WordNetLemmatizer
from scipy.sparse import hstack

app = Flask(__name__)

# Load updated models and vectorizers
headline_model = joblib.load("svm_headline_only.pkl")
combined_model = joblib.load("svm_combined.pkl")
tfidf_headline = joblib.load("tfidf_headline.pkl")
tfidf_article = joblib.load("tfidf_article.pkl")

# Use same weight as training
headline_weight = 5
lemmatizer = WordNetLemmatizer()

def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+|[^a-z\s]|[\d]", "", text)
    return " ".join([lemmatizer.lemmatize(w) for w in text.split()])

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    headline = data.get("headline", "").strip()
    article = data.get("article", "").strip()
    if not headline or not article:
        return jsonify({"error": "Both headline and article are required"}), 400

    h_clean = clean_text(headline)
    a_clean = clean_text(article)

    h_vec = tfidf_headline.transform([h_clean])
    a_vec = tfidf_article.transform([a_clean])
    X_combined = hstack([headline_weight * h_vec, a_vec])

    # Scores
    headline_score = headline_model.decision_function(h_vec)[0]
    combined_score = combined_model.decision_function(X_combined)[0]

    # Give more weight to combined score than headline
    final_score = 0.3 * headline_score + 0.7 * combined_score

    pred = 1 if final_score > 0 else 0

    return jsonify({
        "prediction": "Clickbait" if pred == 1 else "Substance",
        "headline_score": float(headline_score),
        "combined_score": float(combined_score),
        "final_score": float(final_score)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

#llm prompt
getting error in flask so add weight in combined score so that model predicts slightly more on article and headline
