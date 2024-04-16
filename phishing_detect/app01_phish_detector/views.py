from django.shortcuts import render

from django.http import JsonResponse
import joblib
import numpy as np


# Load the trained Random Forest model
rf_model = joblib.load('/Users/perceval/data_science/machine_learning/msc_project/phishing_detect/phishing_random_forest_model.pkl')

# Create your views here.
def index(request):
    page_title = "Home"

def predict(request):
    # Extract features from request
    length = int(request.GET.get('length', ''))
    http = int(request.GET.get('http', ''))
    dots = int(request.GET.get('dots', ''))
        # Make a prediction
    features = np.array([[length, http, dots]])
    prediction = rf_model.predict(features)
    return JsonResponse({'prediction': prediction[0]})


def index(request):
    page_title = "About"

    return render(request, 'app01_phish_detector/index.html', {'page_title': page_title, })

def about(request):
    page_title = "About"
    return render(request, 'app01_phish_detector/about.html', {'page_title': page_title, })
