from django.shortcuts import render

# Create your views here.
def whiteboard_view(request):
    return render(request, 'canvas/index.html')