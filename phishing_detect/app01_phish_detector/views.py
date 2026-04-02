from django.shortcuts import render
import joblib
from .feature_extraction import extract_features

classifier2 = joblib.load('phishing_detector_2.joblib')


def index(request):
    page_title = "Home"
    return render(request, 'app01_phish_detector/index.html', {'page_title': page_title})


def about(request):
    page_title = "About"
    return render(request, 'app01_phish_detector/about.html', {'page_title': page_title})


def result(request):

    page_title = "Result"

    url = request.GET['url']

    features = extract_features(url)

    ans = classifier2.predict([features])[0]

    return render(request,
                  'app01_phish_detector/result.html',
                  {'page_title': page_title,
                   'ans': ans,
                   'url': url})