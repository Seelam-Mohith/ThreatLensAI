"""Email phishing dataset preparation pipeline.

This module is intentionally isolated from URL detection logic.
It handles only email text preprocessing and TF-IDF feature preparation.
"""

from __future__ import annotations

import re
import warnings
from importlib import import_module
from pathlib import Path
from typing import Any, Tuple

import nltk
import numpy as np
import pandas as pd
from nltk.corpus import stopwords
from scipy.sparse import csr_matrix
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATASET = BASE_DIR / "phishing_email.csv"


def _ensure_stopwords_downloaded() -> set[str]:
    """Ensure NLTK stopwords are available and return them as a set."""
    try:
        return set(stopwords.words("english"))
    except LookupError:
        nltk.download("stopwords", quiet=True)
        return set(stopwords.words("english"))


STOP_WORDS = _ensure_stopwords_downloaded()


def load_data(csv_path: str | Path = DEFAULT_DATASET) -> pd.DataFrame:
    """Read CSV, print preview and columns, and return DataFrame."""
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Dataset not found at: {csv_path}")

    df = pd.read_csv(csv_path)
    print("First 5 rows:")
    print(df.head(5))
    print("\nColumn names:")
    print(list(df.columns))
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize columns and clean records for training."""
    text_candidates = ["text", "email", "message", "content", "text_combined", "email_text"]
    label_candidates = ["label", "type", "class", "target", "is_phishing"]

    col_lookup = {col.lower().strip(): col for col in df.columns}

    text_original = next((col_lookup[c] for c in text_candidates if c in col_lookup), None)
    label_original = next((col_lookup[c] for c in label_candidates if c in col_lookup), None)

    if text_original is None:
        raise ValueError(
            "Text column not found. Expected one of: "
            "text, Email, message, content, text_combined, email_text"
        )
    if label_original is None:
        raise ValueError("Label column not found. Expected one of: label, type, class, target, is_phishing")

    standardized = df.rename(columns={text_original: "text", label_original: "label"}).copy()
    standardized = standardized[["text", "label"]]

    standardized = standardized.dropna(subset=["text", "label"])
    standardized["text"] = standardized["text"].astype(str)
    standardized["label"] = standardized["label"].astype(str).str.strip().str.lower()

    # Normalize common label variations to phishing/legitimate.
    label_map = {
        "1": "phishing",
        "0": "legitimate",
        "spam": "phishing",
        "malicious": "phishing",
        "ham": "legitimate",
        "safe": "legitimate",
        "legit": "legitimate",
    }
    standardized["label"] = standardized["label"].replace(label_map)

    print("\nLabel distribution:")
    print(standardized["label"].value_counts(dropna=False))
    return standardized


def preprocess_text(text: str) -> str:
    """Lowercase, remove punctuation/numbers, and remove stopwords."""
    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\d+", " ", text)
    tokens = text.split()
    filtered_tokens = [token for token in tokens if token not in STOP_WORDS]
    return " ".join(filtered_tokens)


def prepare_features(
    csv_path: str | Path = DEFAULT_DATASET,
    test_size: float = 0.2,
    random_state: int = 42,
    max_features: int = 5000,
) -> Tuple[csr_matrix, csr_matrix, pd.Series, pd.Series, TfidfVectorizer]:
    """Build train/test TF-IDF features and return artifacts."""
    df = load_data(csv_path)
    df = clean_data(df)

    df["clean_text"] = df["text"].apply(preprocess_text)

    print("\nSample before and after preprocessing:")
    sample = df[["text", "clean_text"]].head(5)
    for idx, row in sample.iterrows():
        print(f"\nRow {idx}:")
        print("Before:", row["text"])
        print("After :", row["clean_text"])

    x = df["clean_text"]
    y = df["label"]

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )

    vectorizer = TfidfVectorizer(max_features=max_features)
    x_train_tfidf = vectorizer.fit_transform(x_train)
    x_test_tfidf = vectorizer.transform(x_test)

    print("\nFeature matrix shapes:")
    print("X_train_tfidf:", x_train_tfidf.shape)
    print("X_test_tfidf :", x_test_tfidf.shape)
    print("y_train      :", np.asarray(y_train).shape)
    print("y_test       :", np.asarray(y_test).shape)

    return x_train_tfidf, x_test_tfidf, y_train, y_test, vectorizer


def evaluate_model(y_true: pd.Series, y_pred: np.ndarray, model_name: str) -> dict[str, Any]:
    """Compute core metrics for one model and return a result row."""
    return {
        "model": model_name,
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, average="weighted", zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, average="weighted", zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
    }


def train_models(
    x_train_tfidf: csr_matrix,
    x_test_tfidf: csr_matrix,
    y_train: pd.Series,
    y_test: pd.Series,
) -> list[dict[str, Any]]:
    """Train required models, evaluate each, and return unsorted results."""
    models: list[tuple[str, Any]] = [
        ("Logistic Regression (L2)", LogisticRegression(penalty="l2", max_iter=2000, random_state=42)),
        (
            "Logistic Regression (L1)",
            LogisticRegression(penalty="l1", solver="liblinear", max_iter=2000, random_state=42),
        ),
        ("Multinomial Naive Bayes", MultinomialNB()),
        ("SVM (Linear Kernel)", SVC(kernel="linear", random_state=42)),
        ("SVM (RBF Kernel)", SVC(kernel="rbf", random_state=42)),
        ("Decision Tree Classifier", DecisionTreeClassifier(random_state=42)),
        ("Random Forest (n_estimators=100)", RandomForestClassifier(n_estimators=100, random_state=42)),
        ("Random Forest (n_estimators=200)", RandomForestClassifier(n_estimators=200, random_state=42)),
        ("Gradient Boosting Classifier", GradientBoostingClassifier(random_state=42)),
    ]

    try:
        xgb_module = import_module("xgboost")
        xgb_classifier_cls = getattr(xgb_module, "XGBClassifier")
        models.append(
            (
                "XGBoost Classifier",
                xgb_classifier_cls(
                    n_estimators=200,
                    learning_rate=0.1,
                    max_depth=6,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    objective="binary:logistic",
                    eval_metric="mlogloss",
                    random_state=42,
                ),
            )
        )
    except (ImportError, AttributeError):
        print("Warning: xgboost is not installed. Skipping XGBoost Classifier.")

    results: list[dict[str, Any]] = []

    for model_name, model in models:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            if model_name == "Gradient Boosting Classifier":
                x_train_input = x_train_tfidf.toarray()
                x_test_input = x_test_tfidf.toarray()
                model.fit(x_train_input, y_train)
                y_pred = model.predict(x_test_input)
            elif model_name == "XGBoost Classifier":
                encoder = LabelEncoder()
                y_train_encoded = encoder.fit_transform(y_train)
                model.fit(x_train_tfidf, y_train_encoded)
                y_pred_encoded = model.predict(x_test_tfidf)
                y_pred = encoder.inverse_transform(y_pred_encoded.astype(int))
            else:
                model.fit(x_train_tfidf, y_train)
                y_pred = model.predict(x_test_tfidf)

        results.append(evaluate_model(y_test, y_pred, model_name))

    return results


def get_leaderboard(results: list[dict[str, Any]]) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Sort model results by f1 desc, print leaderboard, and return best model."""
    leaderboard = pd.DataFrame(results).sort_values(by="f1", ascending=False).reset_index(drop=True)
    best_model = leaderboard.iloc[0].to_dict()

    print("\nModel Leaderboard (sorted by F1-score):")
    display_df = leaderboard.copy()
    for metric in ["accuracy", "precision", "recall", "f1"]:
        display_df[metric] = display_df[metric].map(lambda x: f"{x:.4f}")
    print(display_df.to_string(index=False))

    print("\nBest Model:")
    print(
        f"{best_model['model']} | "
        f"accuracy={best_model['accuracy']:.4f}, "
        f"precision={best_model['precision']:.4f}, "
        f"recall={best_model['recall']:.4f}, "
        f"f1={best_model['f1']:.4f}"
    )

    return leaderboard, best_model


if __name__ == "__main__":
    X_train_tfidf, X_test_tfidf, y_train, y_test, _ = prepare_features(DEFAULT_DATASET)
    all_results = train_models(X_train_tfidf, X_test_tfidf, y_train, y_test)
    get_leaderboard(all_results)
