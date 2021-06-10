from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import NewUserForm
from .models import Bookshelf, RentalList
from django.contrib.auth.models import User
from .filters import UserFilter
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required


# Create your views here.
def home_page(request):
    username = request.user
    return render(request, 'main_library/home_page.html', {'login': username})


def index(request):
    obj = Bookshelf.objects.values('title', 'author', 'genre', 'kind', 'epoch', 'quantity', 'id')
    table_filter = UserFilter(request.GET, queryset=obj)
    # obj = myFilter.qs
    return render(
        request,
        'main_library/index.html',
        {'all_books': obj, 'table_filter': table_filter}
    )


@login_required
def details(request, id):
    book_details = Bookshelf.objects.get(pk=id)
    return render(
        request,
        "main_library/details.html",
        {'book_details': book_details}
    )


def login_request(request):
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')
    form = AuthenticationForm()
    return render(request=request,
                  template_name="main_library/login.html",
                  context={"form": form})


def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Rejestracja powiodła się.")
            return redirect("home_page")
        messages.error(request, "Ups coś poszło nie tak.")
    form = NewUserForm
    return render(request=request, template_name="main_library/register.html", context={"register_form": form})


def logout_request(request):
    logout(request)
    return redirect('/')


def rent(request, id):
    user_id = User.objects.get(pk=request.user.id)
    username = request.user.username

    if request.method == 'POST':

        # start = request.POST['start_date']
        end = request.POST['end_date']
        book_id = Bookshelf.objects.get(pk=id)

        if book_id.quantity > 0:
            book_id.quantity -= 1
            book_id.save()

            RentalList.objects.create(book_id=book_id, user_id=user_id,
                                      planned_date_of_return=end)
            return render(request, 'main_library/successful_rent.html', {'book': book_id,
                                                                         })
        else:
            return render(request, 'main_library/failed_rent.html', {'book': book_id,
                                                                     })

    return render(request, 'main_library/rent.html', {'user_id': user_id,
                                                      'username': username})


def user_view(request):

    if request.user.is_authenticated:
        user_id = User.objects.get(pk = request.user.id)
        books = RentalList.objects.filter(user_id = request.user.id).order_by('status', '-date_of_return')
            # filter(user_id_id = user_id
        return render(request, 'main_library/user_view.html', {'name': request.user.username, 'books': books})
    else:
        return redirect("login")

def return_book(request, id):
    list_postition_to_return = RentalList.objects.get(pk = id)
    if list_postition_to_return.status == 'Active':
        list_postition_to_return.status = 'Returned'
        list_postition_to_return.date_of_return = datetime.now()
        list_postition_to_return.save()

        book_id = list_postition_to_return.book_id
        book_id.quantity +=1
        book_id.save()

        return redirect("user_view") 
    return redirect("user_view") 

