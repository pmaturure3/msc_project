from django.shortcuts import render
from django.http import JsonResponse
import joblib



# Create your views here.

def index(request):
    page_title = "Home"

    return render(request, 'app01_phish_detector/index.html', {'page_title': page_title, })

def about(request):
    page_title = "About"
    return render(request, 'app01_phish_detector/about.html', {'page_title': page_title, })

def result(request):
    page_title = "Result"

    # cls = joblib.load('phishing_detector_2.joblib')

    classifier2 = joblib.load('phishing_detector_2.joblib')
    
    lis =[]

    lis.append(request.GET['01'])
    lis.append(request.GET['02'])
    lis.append(request.GET['03'])
    lis.append(request.GET['04'])
    lis.append(request.GET['05'])
    lis.append(request.GET['06'])
    lis.append(request.GET['07'])
    lis.append(request.GET['08'])
    lis.append(request.GET['09'])
    lis.append(request.GET['10'])
    lis.append(request.GET['11'])
    lis.append(request.GET['12'])
    lis.append(request.GET['13'])


    print(lis)
    ans = classifier2.predict([lis])

    return render(request, 'app01_phish_detector/result.html', {'page_title': page_title, 'ans':ans})

