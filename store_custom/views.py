from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from django.core.checks import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect

from store.models import Product, Collection


def profile_view(request):
    # Render the profile page with the current user's information
    user = request.user
    if user.is_authenticated:
        context = {
            'user': user,
        }
        return render(request, 'store_custom/profile.html', context)
    else:
        return redirect('login')


def product_list(request):
    collections = Collection.objects.all()
    collection_id = request.GET.get('collection')
    query = request.GET.get('query')

    if collection_id:
        products_list = Product.objects.filter(collection_id=collection_id)
    elif query:
        products_list = Product.objects.filter(
            Q(title__icontains=query) | Q(collection__title__icontains=query)
        )
    else:
        products_list = Product.objects.all()

    paginator = Paginator(products_list, 30)
    page = request.GET.get('page')
    products_request = paginator.get_page(page)

    context = {
        'collections': collections,
        'products': products_request,
        'query': query,
    }
    return render(request, 'store_custom/products.html', context)


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('product_list')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'store_custom/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def register_view(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('product_list')
    context = {'form': form}
    return render(request, 'store_custom/register.html', context)
