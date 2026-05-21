"""Evaluate phishing models on a new/test dataset"""
import pandas as pd
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
import warnings
warnings.filterwarnings('ignore')

from ml.email.email_model import prepare_features, preprocess_text, evaluate_model as email_evaluate
from ml.url.url_model import prepare_url_features, evaluate_model as url_evaluate


def evaluate_email_model(new_dataset_path):
    """Evaluate email phishing model on a new dataset"""
    print("\n" + "="*80)
    print("EMAIL MODEL EVALUATION ON NEW DATASET")
    print("="*80)
    
    # Load and prepare training data to get vectorizer
    print("\n[Step 1] Loading training data to get vectorizer...")
    X_train_tfidf, X_test_tfidf, y_train, y_test, vectorizer = prepare_features('ml/email/phishing_email.csv')
    
    # Load new dataset
    print(f"\n[Step 2] Loading new test dataset: {new_dataset_path}")
    try:
        df_new = pd.read_csv(new_dataset_path)
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return None
    
    # Clean the new dataset (same logic as training)
    print("\n[Step 3] Preprocessing new dataset...")
    text_candidates = ["text", "email", "message", "content", "text_combined", "email_text"]
    label_candidates = ["label", "type", "class", "target", "is_phishing"]
    
    col_lookup = {col.lower().strip(): col for col in df_new.columns}
    text_col = next((col_lookup[c] for c in text_candidates if c in col_lookup), None)
    label_col = next((col_lookup[c] for c in label_candidates if c in col_lookup), None)
    
    if not text_col or not label_col:
        print(f"❌ Could not find text and label columns. Available: {df_new.columns.tolist()}")
        return None
    
    df_clean = df_new[[text_col, label_col]].copy()
    df_clean.columns = ['text', 'label']
    df_clean = df_clean.dropna(subset=['text', 'label'])
    df_clean['text'] = df_clean['text'].astype(str)
    df_clean['label'] = df_clean['label'].astype(str).str.strip().str.lower()
    
    # Normalize labels (same as training)
    label_map = {
        "1": "phishing", "0": "legitimate", "spam": "phishing",
        "malicious": "phishing", "ham": "legitimate", "safe": "legitimate", "legit": "legitimate",
    }
    df_clean['label'] = df_clean['label'].replace(label_map)
    
    print(f"New dataset shape: {df_clean.shape}")
    print(f"Label distribution:\n{df_clean['label'].value_counts()}")
    
    # Preprocess text
    df_clean['clean_text'] = df_clean['text'].apply(preprocess_text)
    
    # Vectorize
    print("\n[Step 4] Vectorizing with trained vectorizer...")
    X_new = vectorizer.transform(df_clean['clean_text'])
    y_new = df_clean['label']
    
    # Train best model on original training data
    print("\n[Step 5] Training best model (Logistic Regression)...")
    best_model = LogisticRegression(penalty='l2', max_iter=2000, random_state=42)
    best_model.fit(X_train_tfidf, y_train)
    
    # Predict on new dataset
    print("\n[Step 6] Making predictions on new dataset...")
    y_pred = best_model.predict(X_new)
    
    # Evaluate
    result = email_evaluate(y_new, y_pred, "Email Model on New Dataset")
    
    print("\n" + "="*80)
    print("RESULTS - EMAIL MODEL ON NEW DATASET")
    print("="*80)
    print(f"Accuracy:  {result['accuracy']:.4f} ({result['accuracy']*100:.2f}%)")
    print(f"Precision: {result['precision']:.4f}")
    print(f"Recall:    {result['recall']:.4f}")
    print(f"F1-Score:  {result['f1']:.4f}")
    print(f"Samples:   {len(y_new)}")
    print("="*80)
    
    return result


def evaluate_url_model(new_dataset_path):
    """Evaluate URL phishing model on a new dataset"""
    print("\n" + "="*80)
    print("URL MODEL EVALUATION ON NEW DATASET")
    print("="*80)
    
    # Load and prepare training data to get vectorizer
    print("\n[Step 1] Loading training data to get vectorizer...")
    X_train_tfidf, X_test_tfidf, y_train, y_test, vectorizer = prepare_url_features('ml/url/malicious_phish.csv')
    
    # Load new dataset
    print(f"\n[Step 2] Loading new test dataset: {new_dataset_path}")
    try:
        df_new = pd.read_csv(new_dataset_path)
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return None
    
    # Clean the new dataset (same logic as training)
    print("\n[Step 3] Preprocessing new dataset...")
    df_new.columns = df_new.columns.str.lower().str.strip()
    
    url_col = None
    label_col = None
    possible_url_cols = ['url', 'link', 'domain', 'website']
    possible_label_cols = ['label', 'class', 'target', 'phishing', 'type', 'status']
    
    for col in df_new.columns:
        if any(x in col for x in possible_url_cols):
            url_col = col
        if any(x in col for x in possible_label_cols):
            label_col = col
    
    if not url_col or not label_col:
        print(f"❌ Could not find URL and label columns. Available: {df_new.columns.tolist()}")
        return None
    
    df_clean = df_new[[url_col, label_col]].copy()
    df_clean.columns = ['url', 'label']
    df_clean = df_clean.dropna()
    df_clean['label'] = df_clean['label'].astype(str).str.lower().str.strip()
    
    # Normalize labels
    def categorize_threat(val):
        val_lower = str(val).lower()
        if 'phishing' in val_lower:
            return 'phishing'
        elif 'malware' in val_lower:
            return 'malware'
        elif 'defacement' in val_lower:
            return 'defacement'
        elif 'benign' in val_lower or 'legitimate' in val_lower or 'safe' in val_lower:
            return 'benign'
        return str(val)
    
    df_clean['label'] = df_clean['label'].apply(categorize_threat)
    valid_labels = ['phishing', 'malware', 'defacement', 'benign']
    df_clean = df_clean[df_clean['label'].isin(valid_labels)].copy()
    
    print(f"New dataset shape: {df_clean.shape}")
    print(f"Label distribution:\n{df_clean['label'].value_counts()}")
    
    # Vectorize
    print("\n[Step 4] Vectorizing with trained vectorizer...")
    X_new = vectorizer.transform(df_clean['url'].values)
    y_new = df_clean['label'].values
    
    # Train best model on original training data
    print("\n[Step 5] Training best model (Logistic Regression)...")
    best_model = LogisticRegression(penalty='l2', max_iter=1000, random_state=42)
    best_model.fit(X_train_tfidf, y_train)
    
    # Predict on new dataset
    print("\n[Step 6] Making predictions on new dataset...")
    y_pred = best_model.predict(X_new)
    
    # Evaluate
    result = url_evaluate(y_new, y_pred, "URL Model on New Dataset")
    
    print("\n" + "="*80)
    print("RESULTS - URL MODEL ON NEW DATASET")
    print("="*80)
    print(f"Accuracy:  {result['accuracy']:.4f} ({result['accuracy']*100:.2f}%)")
    print(f"Precision: {result['precision']:.4f}")
    print(f"Recall:    {result['recall']:.4f}")
    print(f"F1-Score:  {result['f1']:.4f}")
    print(f"Samples:   {len(y_new)}")
    print("="*80)
    
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python evaluate_on_new_dataset.py <model_type> <dataset_path>")
        print("\nmodel_type: 'email' or 'url'")
        print("dataset_path: path to your new CSV dataset")
        print("\nExamples:")
        print("  python evaluate_on_new_dataset.py email new_emails.csv")
        print("  python evaluate_on_new_dataset.py url new_urls.csv")
        sys.exit(1)
    
    model_type = sys.argv[1].lower()
    dataset_path = sys.argv[2]
    
    if model_type == 'email':
        evaluate_email_model(dataset_path)
    elif model_type == 'url':
        evaluate_url_model(dataset_path)
    else:
        print(f"❌ Invalid model type: {model_type}. Use 'email' or 'url'")
        sys.exit(1)
