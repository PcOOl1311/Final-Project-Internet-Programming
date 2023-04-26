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
    # Get the authenticated user
    user = request.user

    # Create a form instance with the user's profile data
    form = UserProfileForm(instance=user)

    # Disable form fields by setting the `disabled` attribute to True
    for field in form.fields.values():
        field.disabled = True

    # Render the profile view with the form
    return render(request, 'store_custom/profile.html', {'form': form})


@login_required
def edit_profile_view(request):
    # Get the authenticated user
    user = request.user

    # Check if the form has been submitted
    if request.method == 'POST':
        # Create a form instance with the submitted data and the user instance
        form = EditProfileForm(request.POST, instance=user)

        # Check if the form data is valid
        if form.is_valid():
            # Save the form data
            form.save()
            # Redirect to the profile page
            return redirect('profile')
    else:
        # Create a form instance with the user's profile data
        form = EditProfileForm(instance=user)

    # Render the edit profile view with the form
    return render(request, 'store_custom/edit_profile.html', {'form': form})


def product_list(request):
    # Get all collections
    collections = Collection.objects.all()

    # Get the `collection` and `query` parameters from the request
    collection_id = request.GET.get('collection')
    query = request.GET.get('query')

    # Filter products based on the `collection_id` or `query` parameter
    if collection_id:
        products_list = Product.objects.filter(collection_id=collection_id)
    elif query:
        # Sanitize the query parameter before using it in the filter
        query = query.strip()
        products_list = Product.objects.filter(
            Q(title__icontains=query) | Q(collection__title__icontains=query)
        )
    else:
        products_list = Product.objects.all()

    # Paginate the products list
    paginator = Paginator(products_list, 30)
    page = request.GET.get('page')
    product_page = paginator.get_page(page)

    # Render the product list view with the filtered and paginated products
    context = {
        'collections': collections,
        'products': product_page,
        'query': query,
    }
    return render(request, 'store_custom/products.html', context)


def login_view(request):
    if request.method == 'POST':
        # Get the username and password from the request
        username = request.POST['username']
        password = request.POST['password']

        # Authenticate the user with the username and password
        user = authenticate(request, username=username, password=password)

        # If the authentication is successful, log the user in and redirect to the product list page
        if user is not None:
            login(request, user)
            return redirect('product_list')
        else:
            # If the authentication fails, display an error message
            messages.error(request, 'Invalid username or password')
            return render(request, 'store_custom/login.html', {'show_alert': True})

    # Render the login view
    return render(request, 'store_custom/login.html')


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
    # Log the user out and redirect to the login page
    logout(request)
    return redirect('login')


def register_view(request):
    if request.method == 'POST':
        # Create a form instance with the submitted data
        form = UserRegistrationForm(request.POST)

        # Check if the form data is valid
        if form.is_valid():
            # Save the form data and get the new user's username
            form.save()
            username = form.cleaned_data.get('username')
            # Display a success message and redirect to the login page
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        # Create an empty form instance
        form = UserRegistrationForm()

    # Render the registration view with the form
    return render(request, 'store_custom/register.html', {'form': form})
