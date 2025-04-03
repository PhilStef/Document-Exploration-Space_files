import os
import json
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
import spacy
import nltk
from nltk.corpus import words
import re

# Load spaCy
nlp = spacy.load("en_core_web_sm")

# English word set
english_vocab = set(w.lower() for w in words.words())

def clean_text(text):
    text = re.sub(r'base\d+', '', text)
    text = re.sub(r'ui-id-\d+', '', text)
    text = re.sub(r'\b(ui|id)\b', '', text)
    return text.lower().strip()

def extract_named_entities(texts):
    entities = []
    for text in texts:
        doc = nlp(text)
        entities.extend([ent.text for ent in doc.ents])
    return entities

def compute_batch_tfidf(texts, top_n=10):
    cleaned = [clean_text(t) for t in texts]
    
    filtered = []
    for text in cleaned:
        tokens = re.findall(r'\b[a-z]+\b', text)
        words_only = [w for w in tokens if w in english_vocab or len(w) > 2]
        filtered.append(' '.join(words_only))

    vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
    tfidf_matrix = vectorizer.fit_transform(filtered)
    feature_names = vectorizer.get_feature_names_out()

    # Compute average TF-IDF score per term
    avg_scores = tfidf_matrix.mean(axis=0).A1  # mean keeps values in 0-1 range
    top_indices = avg_scores.argsort()[::-1][:top_n]
    top_terms = [(feature_names[i], avg_scores[i]) for i in top_indices]
    return top_terms


def plot_top_terms(batch_id, top_terms, output_dir="plots_by_batch"):
    os.makedirs(output_dir, exist_ok=True)
    terms, scores = zip(*top_terms)
    plt.figure(figsize=(10, 6))
    plt.barh(terms[::-1], scores[::-1])
    plt.xlabel("TF-IDF Score")
    plt.title(f"Top 10 TF-IDF Terms for Batch {batch_id}")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"batch_{batch_id}_top_terms.png"))
    plt.close()

def main():
    filepath = "explorer/data/Maverick/MavOutput.json"
    with open(filepath, "r") as f:
        data = json.load(f)

    # Group documents by batch
    batch_map = {}
    all_texts = []
    for doc in data:
        batch = doc.get("batch", "unknown")
        batch_map.setdefault(batch, []).append(doc)
        all_texts.append(doc.get("contents", ""))

    for batch_id, docs in batch_map.items():
        print(f"Processing Batch {batch_id} with {len(docs)} documents...")
        texts = [doc.get("contents", "") for doc in docs]
        top_terms = compute_batch_tfidf(texts)
        plot_top_terms(batch_id, top_terms)

    # 🆕 Combined chart for all batches
    print("Processing combined chart for all batches...")
    combined_top_terms = compute_batch_tfidf(all_texts)
    plot_top_terms("all_batches", combined_top_terms)


if __name__ == "__main__":
    main()
