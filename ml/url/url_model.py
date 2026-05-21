import pandas as pd
import numpy as np
from pathlib import Path
import time
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import xgboost as xgb

# ============ DATA LOADING ============

def load_url_data(csv_path):
    """Load URL phishing dataset"""
    df = pd.read_csv(csv_path)
    print("\nDataset Loaded Successfully!")
    print(f"Shape: {df.shape}")
    print(f"\nFirst 5 rows:")
    print(df.head())
    print(f"\nColumn names: {df.columns.tolist()}")
    
    # Display preview
    print(f"\nData types:\n{df.dtypes}")
    return df

# ============ DATA PREPROCESSING ============

def clean_url_data(df):
    """Clean and standardize URL dataset"""
    # Standardize column names
    df.columns = df.columns.str.lower().str.strip()
    
    # Identify URL and label columns (flexible naming)
    url_col = None
    label_col = None
    
    possible_url_cols = ['url', 'link', 'domain', 'website']
    possible_label_cols = ['label', 'class', 'target', 'phishing', 'type', 'status']
    
    for col in df.columns:
        if any(x in col for x in possible_url_cols):
            url_col = col
        if any(x in col for x in possible_label_cols):
            label_col = col
    
    if not url_col or not label_col:
        print(f"Available columns: {df.columns.tolist()}")
        raise ValueError("Could not find URL and label columns")
    
    # Create working dataframe
    df_clean = df[[url_col, label_col]].copy()
    df_clean.columns = ['url', 'label']
    
    print(f"\nUsing columns: url='{url_col}', label='{label_col}'")
    
    # Normalize labels
    df_clean['label'] = df_clean['label'].astype(str).str.lower().str.strip()
    
    # For multi-class: map to threat categories
    # Simplify to: phishing, malware, defacement, benign
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
    
    # Remove invalid entries
    valid_labels = ['phishing', 'malware', 'defacement', 'benign']
    df_clean = df_clean[df_clean['label'].isin(valid_labels)].copy()
    df_clean = df_clean.dropna()
    
    print(f"\nLabel distribution after cleaning:")
    print(df_clean['label'].value_counts())
    
    return df_clean

def extract_url_features(url_string):
    """Extract meaningful features from URL for analysis"""
    # Just use the URL as-is, TF-IDF will handle feature extraction
    return str(url_string)

def prepare_url_features(csv_path, test_size=0.2, max_features=5000):
    """Prepare TF-IDF features for URL data"""
    df = load_url_data(csv_path)
    df = clean_url_data(df)
    
    # Use URLs directly as text features
    print("\nPreparing URL text features...")
    X = df['url'].values
    y = df['label'].values
    
    # Split data with stratification
    print(f"Splitting data: {test_size*100}% test, {(1-test_size)*100}% train")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, stratify=y, random_state=42
    )
    
    # TF-IDF vectorization
    print(f"\nTF-IDF Vectorization (max features: {max_features})...")
    vectorizer = TfidfVectorizer(max_features=max_features, stop_words='english')
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    
    print(f"Feature matrix shapes:")
    print(f"X_train_tfidf: {X_train_tfidf.shape}")
    print(f"X_test_tfidf : {X_test_tfidf.shape}")
    print(f"y_train      : {y_train.shape}")
    print(f"y_test       : {y_test.shape}")
    
    return X_train_tfidf, X_test_tfidf, y_train, y_test, vectorizer

# ============ MODEL EVALUATION ============

def evaluate_model(y_true, y_pred, model_name):
    """Evaluate model performance"""
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
    
    return {
        'model': model_name,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
    }

# ============ MODEL TRAINING ============

def train_url_models(X_train_tfidf, X_test_tfidf, y_train, y_test):
    """Train multiple URL detection models"""
    models = {
        'Logistic Regression (L2)': LogisticRegression(penalty='l2', max_iter=1000, random_state=42),
        'SVM (Linear, LinearSVC)': LinearSVC(max_iter=2000, random_state=42, dual=False),
        'Random Forest (n_estimators=50)': RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
        'Multinomial Naive Bayes': MultinomialNB(),
        'Decision Tree': DecisionTreeClassifier(random_state=42),
        'XGBoost Classifier': xgb.XGBClassifier(n_estimators=100, random_state=42, verbosity=0, n_jobs=-1),
    }
    
    results = []
    
    print("\n" + "="*60)
    print("Training URL Detection Models (7 ML Models)")
    print("="*60)
    
    for name, model in models.items():
        try:
            start_time = time.time()
            print(f"\n🔄 Training: {name}...", end=" ", flush=True)
            
            model.fit(X_train_tfidf, y_train)
            y_pred = model.predict(X_test_tfidf)
            
            elapsed = time.time() - start_time
            row = evaluate_model(y_test, y_pred, name)
            row['train_seconds'] = round(elapsed, 2)
            results.append(row)
            
            print(f"✓ F1: {row['f1']:.6f} ({elapsed:.2f}s)")
        
        except Exception as e:
            print(f"✗ Error: {str(e)[:50]}")
            continue
    
    return results

# ============ LEADERBOARD ============

def get_url_leaderboard(results):
    """Sort and display leaderboard"""
    df = pd.DataFrame(results)
    df_sorted = df.sort_values(by='f1', ascending=False).reset_index(drop=True)
    
    print("\n" + "="*80)
    print("URL DETECTION MODEL LEADERBOARD (Sorted by F1 Score)")
    print("="*80)
    print(df_sorted.to_string(index=False))
    print("="*80)
    
    return df_sorted

# ============ MAIN ============

if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════════╗
    ║   ThreatLens AI - URL Model Trainer    ║
    ║   Training Phishing URL Detection      ║
    ║   7 Machine Learning Models            ║
    ╚════════════════════════════════════════╝
    """)
    
    # Path to URL dataset
    csv_path = Path('ml/url/malicious_phish.csv')
    
    if not csv_path.exists():
        print(f"\n❌ Dataset not found: {csv_path}")
        print("\nTo train URL models:")
        print("1. Download a URL phishing dataset from Kaggle")
        print("   Example: https://www.kaggle.com/datasets/sid321axn/malicious-urls-dataset")
        print("2. Place the CSV file at: ml/url/malicious_phish.csv")
        print("3. Ensure the CSV has columns for 'url' and 'type/label'")
        print("4. Run this script again")
        exit(1)
    
    try:
        start = time.time()
        
        # Prepare features
        X_train, X_test, y_train, y_test, vectorizer = prepare_url_features(csv_path)
        
        # Train models
        results = train_url_models(X_train, X_test, y_train, y_test)
        
        # Display leaderboard
        leaderboard = get_url_leaderboard(results)
        
        total_time = time.time() - start
        print(f"\n⏱️  Total training time: {total_time:.2f} seconds")
        
    except Exception as e:
        print(f"\n❌ Error during training: {str(e)}")
        import traceback
        traceback.print_exc()
