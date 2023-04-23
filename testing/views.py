from django.shortcuts import render

from store.models import *


def say_hello(request):
    # show all products
    products = Product.objects.all()

    return render(request, 'hello.html', {'name': 'Kostas', 'products': products})
