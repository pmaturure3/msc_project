import os
from django.shortcuts import render
import joblib
import numpy as np
from .feature_extraction import extract_features
from .models import URLCheck

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model = joblib.load(os.path.join(BASE_DIR, 'phishing_hybrid_voting_hard.pkl'))
scaler = joblib.load(os.path.join(BASE_DIR, 'standard_scaler.pkl'))
feature_names = joblib.load(os.path.join(BASE_DIR, 'feature_names.pkl'))


def index(request):
    page_title = "Home"
    return render(request, 'app01_phish_detector/index.html', {'page_title': page_title})


def about(request):
    page_title = "About"
    return render(request, 'app01_phish_detector/about.html', {'page_title': page_title})


def result(request):
    page_title = "Result"

    # Get the URL submitted by the user
    url = request.GET.get('url', '')

    # Extract all features from the URL
    features_dict = extract_features(url)

    # Check for any missing features before prediction
    missing = [f for f in feature_names if f not in features_dict]
    if missing:
        print(f"WARNING: Missing features in extract_features(): {missing}")
        print(f"Available features: {sorted(features_dict.keys())}")
        print(f"Expected features: {feature_names}")
        raise KeyError(
            f"feature_extraction.py is missing these features: {missing}. "
            f"Add them to the extract_features() function."
        )

    # Ensure features are in the exact same order as the training data
    features = [features_dict[feat] for feat in feature_names]

    # Scale the features using the same scaler fitted during training
    features_scaled = scaler.transform([features])

    # Predict using the loaded hybrid voting model
    ans = model.predict(features_scaled)[0]

    # Save to database
    URLCheck.objects.create(url=url, is_phishing=bool(ans))

    # Render the result page with the prediction
    return render(
        request,
        'app01_phish_detector/result.html',
        {
            'page_title': page_title,
            'ans': ans,
            'url': url
        }
    )