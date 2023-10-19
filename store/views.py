from django.shortcuts import render


# Create your views here.
def home(request):
    context = {
        'value': 'store'
    }
    return render(request, 'base.html', context)