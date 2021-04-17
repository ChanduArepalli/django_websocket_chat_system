from django.shortcuts import render

# Create your views here.
def index(request, username=None):
    return render(request, template_name='index.html')