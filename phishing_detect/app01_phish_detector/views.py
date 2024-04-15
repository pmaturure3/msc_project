from django.shortcuts import render

# Create your views here.
def index(request):
    page_title = "Home"
    return render(request, 'app01_phish_detector/index.html', {'page_title': page_title, })
