from django.http import HttpResponse

def register(request):
    return HttpResponse("Register sayfası")

def login_view(request):
    return HttpResponse("Login sayfası")

def logout_view(request):
    return HttpResponse("Logout sayfası")
