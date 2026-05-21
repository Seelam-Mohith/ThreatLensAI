from pathlib import Path
import time
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
from ml.email.email_model import prepare_features, evaluate_model

start = time.time()
X_train_tfidf, X_test_tfidf, y_train, y_test, _ = prepare_features(Path('ml/email/phishing_email.csv'))

# Encode labels for XGBoost
le = LabelEncoder()
y_train_enc = le.fit_transform(y_train)
y_test_enc = le.transform(y_test)

models = [
    ("Logistic Regression (L2)", LogisticRegression(penalty='l2', max_iter=2000, random_state=42), y_train, y_test),
    ("SVM (Linear, LinearSVC)", LinearSVC(random_state=42, max_iter=5000), y_train, y_test),
    ("Multinomial Naive Bayes", MultinomialNB(), y_train, y_test),
    ("XGBoost Classifier", XGBClassifier(n_estimators=100, learning_rate=0.1, max_depth=6, random_state=42, eval_metric='logloss', verbosity=0), y_train_enc, y_test_enc),
    ("Random Forest (n_estimators=50)", RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1), y_train, y_test),
]

results = []
for name, model, y_tr, y_te in models:
    t0 = time.time()
    model.fit(X_train_tfidf, y_tr)
    y_pred_raw = model.predict(X_test_tfidf)
    # Convert back to original labels if needed
    if name == "XGBoost Classifier":
        y_pred = le.inverse_transform(y_pred_raw.astype(int))
        y_te_eval = le.inverse_transform(y_te.astype(int))
    else:
        y_pred = y_pred_raw
        y_te_eval = y_te
    row = evaluate_model(y_te_eval, y_pred, name)
    row['train_seconds'] = round(time.time() - t0, 2)
    results.append(row)
    print(f"✓ {name:40s} - F1: {row['f1']:.6f} ({row['train_seconds']}s)")

leaderboard = pd.DataFrame(results).sort_values(by='f1', ascending=False).reset_index(drop=True)
print('\n\n=== FINAL LEADERBOARD (sorted by F1) ===')
print(leaderboard.to_string(index=False))
print(f'\nTotal runtime: {time.time() - start:.2f} seconds')
