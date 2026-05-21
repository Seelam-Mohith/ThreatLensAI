# URL Phishing Detection Dataset

This directory is for URL phishing detection models.

## Instructions

### 1. Download Dataset

Download a URL phishing dataset from Kaggle:
- **Option 1:** [Phishing URL Dataset](https://www.kaggle.com/datasets/phishingurl/phishing-url-dataset)
- **Option 2:** [Malicious URLs Dataset](https://www.kaggle.com/datasets/sid321axn/malicious-urls-dataset)
- **Option 3:** Any dataset with URL and phishing label columns

### 2. Prepare Dataset

The CSV file should have at least these columns:
- `url` (or: link, domain, website)
- `label` (or: class, target, type, status)

Label values should be:
- `phishing`, `malicious`, `suspicious`, `1`, `bad`, etc. (phishing indicators)
- `legitimate`, `benign`, `safe`, `0`, `good`, etc. (safe indicators)

### 3. Place File

Save the dataset as: **`phishing_urls.csv`**

### 4. Train Models

Run the training script:
```bash
python url_model.py
```

## Expected Output

The script will:
1. Load and clean the dataset
2. Extract URL features using TF-IDF vectorization
3. Train 7 ML models:
   - Logistic Regression (L2)
   - SVM (Linear)
   - Random Forest
   - Gradient Boosting
   - Naive Bayes
   - Decision Tree
   - XGBoost
4. Display model performance leaderboard
5. Show F1 scores and training times

## Sample Datasets

Popular Kaggle datasets for URL phishing detection:

1. **Phishing URL Dataset** (UCI)
   - 88,647 URLs (legitimate and phishing)
   - Features: URL structure, domain info
   - License: Public

2. **Malicious URLs Dataset**
   - 651,191 URLs
   - Categories: benign, defacement, phishing, malware
   - CSV format with URL and type columns

3. **OpenPhish + PhishTank Combined**
   - Real-time threat data
   - Daily updates
   - Community-sourced

## Dataset Format Example

```csv
url,label
http://www.example.com,legitimate
http://phish-example.tk,phishing
https://amazon-secure.xyz/login,phishing
https://google.com,legitimate
```

## After Training

Once trained:
1. Models are evaluated on test set
2. Leaderboard shows best performers
3. Update backend API to use trained models
4. Integrate with frontend URL Analyzer

## Features Extracted

From each URL, the script extracts:
- Scheme (HTTP/HTTPS)
- Domain name
- Path components
- Query parameters
- URL length
- Special characters
- Subdomain count
- And more via TF-IDF

## Model Comparison

The leaderboard will show:
- **Accuracy**: Overall correctness
- **Precision**: False positive rate
- **Recall**: False negative rate
- **F1 Score**: Balanced metric
- **Training Time**: Speed of each model

## Next Steps

1. ✅ Add dataset file
2. ✅ Run training
3. ✅ Review leaderboard
4. ✅ Save best model to `ml/url/best_url_model.pkl`
5. ✅ Update backend to use trained models
