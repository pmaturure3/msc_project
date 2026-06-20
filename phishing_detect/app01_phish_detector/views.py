import os
from django.shortcuts import render
import joblib
import numpy as np
from django.conf import settings
from .feature_extraction import extract_features
from .models import URLCheck

BASE_DIR = settings.BASE_DIR
MODEL_DIR = os.path.join(BASE_DIR, 'app01_phish_detector', 'trained_models')

model = joblib.load(os.path.join(MODEL_DIR, 'phishing_hybrid_soft.pkl'))
scaler = joblib.load(os.path.join(MODEL_DIR, 'scaler.pkl'))
feature_names = joblib.load(os.path.join(MODEL_DIR, 'feature_names.pkl'))

def index(request):
    page_title = "Home"
    return render(request, 'app01_phish_detector/index.html', {'page_title': page_title})

def about(request):
    page_title = "About"
    return render(request, 'app01_phish_detector/about.html', {'page_title': page_title})

def result(request):
    page_title = "Result"
    url = request.GET.get('url', '')

    if not url:
        return render(request, 'app01_phish_detector/result.html', {
            'page_title': page_title,
            'error': 'No URL provided'
        })

    try:
        features_dict = extract_features(url)
        missing = [f for f in feature_names if f not in features_dict]
        if missing:
            raise KeyError(f"Missing features: {missing}")

        features = [features_dict[feat] for feat in feature_names]
        features_array = np.array(features).reshape(1, -1)
        features_scaled = scaler.transform(features_array)

        ans = model.predict(features_scaled)[0]
        probabilities = model.predict_proba(features_scaled)[0]
        prob_legitimate = probabilities[0]
        prob_phishing = probabilities[1]

        URLCheck.objects.create(
            url=url,
            is_phishing=bool(ans),
            probability_legitimate=prob_legitimate,
            probability_phishing=prob_phishing
        )

        return render(request, 'app01_phish_detector/result.html', {
            'page_title': page_title,
            'ans': ans,
            'url': url,
            'prob_legitimate': prob_legitimate,
            'prob_phishing': prob_phishing
        })
    except Exception as e:
        return render(request, 'app01_phish_detector/result.html', {
            'page_title': page_title,
            'error': str(e),
            'url': url
        })