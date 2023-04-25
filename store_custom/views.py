from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import redirect, render

from store.models import Product, Collection
from .forms import UserProfileForm, UserRegistrationForm, EditProfileForm


@login_required
def profile_view(request):
    user = request.user
    if user.is_authenticated:
        # Disable form fields by setting the `disabled` attribute to True.
        form = UserProfileForm(instance=user)
        for field in form.fields.values():
            field.disabled = True
    else:
        redirect('login')
    return render(request, 'store_custom/profile.html', {'form': form})


@login_required
def edit_profile_view(request):
    user = request.user
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = EditProfileForm(instance=user)
    return render(request, 'store_custom/edit_profile.html', {'form': form})


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
            return render(request, 'store_custom/login.html', {'show_alert': True})

    return render(request, 'store_custom/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'store_custom/register.html', {'form': form})
