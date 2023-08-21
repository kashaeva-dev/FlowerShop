from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse('Это сайт магазина цветов FlowerShop')
