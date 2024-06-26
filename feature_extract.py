"""Extract features from text using BERT.
"""

import argparse
import os
import re

import nltk
import pandas as pd
import torch
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from transformers import BertModel, BertTokenizer


# Initialize the lemmatizer and stopwords
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words("english"))


def preprocess_text(text: str) -> str:
    """Preprocess the text by lowercasing, removing punctuation, and stopwords.

    :param text: Text to preprocess.
    :type text: str
    :return: Preprocessed text.
    :rtype: str
    """
    # Lowercase the text
    text = text.lower()

    # Remove punctuation
    text = re.sub(r"[^\w\s]", "", text)

    # Remove stopwords
    tokens = word_tokenize(text)

    text = " ".join([word for word in tokens if word not in stop_words])

    return text


def extract_bert_features(
    texts: list[str], model_name="bert-base-uncased"
) -> torch.Tensor:
    """Extract features from text using a pre-trained BERT model.

    :param texts: List of texts to extract features from.
    :type texts: list[str]
    :param model_name: Model name or version to download, defaults to "bert-base-uncased"
    :type model_name: str, optional
    :return: Extracted features from the text.
    :rtype: torch.Tensor
    """
    # Load pre-trained BERT model and tokenizer
    tokenizer = BertTokenizer.from_pretrained(model_name)
    bert_model = BertModel.from_pretrained(model_name)

    # Tokenize and encode text
    inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=True)

    # Pass input through BERT model
    with torch.no_grad():
        outputs = bert_model(**inputs)
        hidden_states = outputs.last_hidden_state

    # Extract features (average pooling)
    features = hidden_states.mean(dim=1)  # Average pooling across tokens

    return features


def main(download_nltk=False):
    """Run the feature extraction pipeline.

    :param download_nltk: Downloads nltk punk, stopwords and wordnet, defaults to False
    :type download_nltk: bool, optional
    """
    if download_nltk:
        # Download NLTK resources (if not already downloaded)
        nltk.download("punkt")
        nltk.download("stopwords")
        nltk.download("wordnet")

    categories = os.listdir("./articles")
    all_features = []

    for category in categories:
        files = os.listdir(f"./articles/{category}")
        for file in files:
            print(category, file)
            with open(f"./articles/{category}/{file}", "r", encoding="utf-8") as f:
                article = f.read()
                preprocessed_text = preprocess_text(article)
                features = extract_bert_features(preprocessed_text)
                features = features.numpy()

                # Store category, filename, and features
                all_features.append((category, file[:-4], features, article))

    # Create DataFrame from collected features
    df_features = pd.DataFrame(
        all_features, columns=["Category", "Title", "Features", "Text"]
    )
    print(df_features.head())
    df_features.to_csv("features.csv", index=False)


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument(
        "--download-nltk", action="store_true", help="Download NLTK resources"
    )
    main(**vars(args.parse_args()))
