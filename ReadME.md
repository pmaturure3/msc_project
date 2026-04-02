# Hybrid Machine Learning Model for Phishing Detection

---
| | |
|---|---|
| **Programme** | MSc Cyber Security and Forensic Information Technology |
| **School** | University of Portsmouth · School of Computing |
| **Project Title** | Hybrid Machine Learning Model for Phishing Detection |
| **Year** | 2023/24 |
| **Supervisor** | Dr Asim Ali, Assoc Prof Alexander Gegov |
| **Student** | Perceval Maturure |
|**IEEE Conference Paper**| **Maturure, P**., Ali, A., & Gegov, A. (2024). **Hybrid machine learning model for phishing detection**. IEEE. [https://ieeexplore.ieee.org/document/10705257](https://ieeexplore.ieee.org/document/10705257) | 
| **Project URL** | [phish-detect-01.dev.tp-stack.co.uk](https://phish-detect-01.dev.tp-stack.co.uk) |

---

## Project Component 1 – Machine Learning Model

Developed a Hybrid machine learning model for phishing detection.

**Technology:** Python 3, Anaconda, Jupyter Notebook

---

## Project Component 2 – Phishing Detection System

A web application that allows users to submit a URL and receive a real-time prediction of whether it is legitimate or phishing.

**Technology:** Django 4, Python 3, SQLite Database

### How to Run Locally

1. Clone the repository: `git clone <GitHub URL>`
2. Create and activate a virtual environment:
   ```
   python3 -m venv env
   cd env
   source bin/activate
   ```
3. Install dependencies: `pip3 install -r requirements.txt`
4. Run the server: `python3 manage.py runserver`
5. Visit `http://127.0.0.1:8000` in your browser

---

## Changelog

### Version 2.0 – Hybrid Voting Classifier (All 41 Features)

#### 1. New Hybrid Voting Model (`Phishing_Hybrid_Voting.ipynb`)

- Combined the Decision Tree and Random Forest classifiers into a single **Hybrid Voting Classifier** using scikit-learn's `VotingClassifier`.
- Implemented both **Hard Voting** (majority vote) and **Soft Voting** (averaged probabilities) strategies.
- Trained the hybrid model using **all 41 features** from the dataset to maximise detection accuracy and reduce false positives.
- Added comprehensive comparative analysis across all metrics: Accuracy, Precision, Recall, F1-Score, ROC AUC, and MCC.
- Added visualisations: per-metric bar charts, side-by-side confusion matrices, ROC curves, and grouped bar charts.
- Exported trained model artifacts: `phishing_hybrid_voting_hard.pkl`, `phishing_hybrid_voting_soft.pkl`, `standard_scaler.pkl`, and `feature_names.pkl`.

#### 2. Updated Django Application (`views.py`)

- Integrated the Hybrid Voting Classifier (Hard Voting) as the prediction model, replacing the standalone Random Forest model.
- Added **StandardScaler** integration — the scaler fitted during training is now applied to user-submitted URLs before prediction, ensuring feature values match the scale the model was trained on.
- Added feature ordering using `feature_names.pkl` to guarantee features are passed to the model in the exact same column order as during training.
- Used absolute file paths (`os.path`) for loading `.pkl` files, fixing `FileNotFoundError` issues caused by Django's working directory.
- Added missing feature validation with clear error messages to help debug any mismatches between the model's expected features and the extracted features.

#### 3. New Feature Extraction Module (`feature_extraction.py`)

- Created a new module that automatically extracts all 41 URL features from any user-submitted URL.
- Features are extracted by parsing the URL and computing:
  - Character counts (dots, hyphens, underlines, slashes, special characters, digits)
  - Domain and subdomain analysis (length, digit presence, repeated digits, special characters)
  - Path, query, fragment, and anchor detection
  - Shannon entropy calculations for both the full URL and domain
- Returns a dictionary of features which is then ordered by `feature_names.pkl` to match the training data column order.

#### 4. Why All 41 Features Instead of 13

The initial version used only 13 features selected from feature importance analysis. This caused **false positives** where legitimate URLs (e.g., `amazon.co.uk`) were incorrectly flagged as phishing. Switching to all 41 features provides the model with richer contextual information, reducing misclassifications and improving overall prediction reliability.

---

## Resources

- [Django Tutorial – Tech with Tim](https://www.youtube.com/watch?v=uu98pqiUJU8&list=PLEsfXFp6DpzTD1BD1aWNxS2Ep06vIkaeW)
- [Django Tutorial – Corey Schafer](https://www.youtube.com/watch?v=UmljXZIypDc&list=PL-osiE80TeTtoQCKZ03TU5fNfx2UY6U4p)