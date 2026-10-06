"""Train and save the complaint category classifier."""

from pathlib import Path
import pickle

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "complaints_dataset.csv"
MODEL_PATH = BASE_DIR / "complaint_model.pkl"


def train() -> None:
    data = pd.read_csv(DATA_PATH)
    required = {"complaint", "category"}
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")

    model = Pipeline([
        ("tfidf", TfidfVectorizer(lowercase=True, ngram_range=(1, 2), sublinear_tf=True)),
        ("classifier", LogisticRegression(max_iter=2000, random_state=42)),
    ])
    model.fit(data["complaint"], data["category"])

    with MODEL_PATH.open("wb") as file:
        pickle.dump(model, file, protocol=pickle.HIGHEST_PROTOCOL)

    print(f"Model trained successfully: {MODEL_PATH}")


if __name__ == "__main__":
    train()
