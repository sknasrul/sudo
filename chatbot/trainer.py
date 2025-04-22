import json
import random
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer

nltk.download('punkt')
nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()
with open("data/intents.json") as f:
    data = json.load(f)

corpus, labels = [], []

for intent in data["intents"]:
    for pattern in intent["patterns"]:
        tokens = nltk.word_tokenize(pattern)
        tokens = [lemmatizer.lemmatize(w.lower()) for w in tokens]
        corpus.append(" ".join(tokens))
        labels.append(intent["tag"])

vectorizer = CountVectorizer()
X = vectorizer.fit_transform(corpus)
clf = MultinomialNB()
clf.fit(X, labels)

# Save model
with open("chatbot/model.pkl", "wb") as f:
    pickle.dump((clf, vectorizer, data), f)
