from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import CarDealer, CarMake, CarModel
from .models import CarDealer, CarMake, CarModel
from .restapis import get_dealers_from_cf, get_request, get_dealer_reviews_from_cf, post_request
# from .restapis import get_dealers_from_cf, get_request, post_request


from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact_us.html', context)

# Create a `login_request` view to handle sign in request


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/user_login_bootstrap.html', context)
    else:
        return render(request, 'djangoapp/user_login_bootstrap.html', context)

# Create a `logout_request` view to handle sign out request


def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request


def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships


def get_dealerships(request):
    context = {}
    if request.method == "GET":
        #url = "your-cloud-function-domain/dealerships/dealer-get"
        url = "https://586dc592.us-south.apigw.appdomain.cloud/api/dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        context["dealership_list"] = dealerships
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name

        return render(request, 'djangoapp/index.html', context=context)


# def get_dealerships(request):
#     if request.method == "GET":
#         url = "https://586dc592.us-south.apigw.appdomain.cloud/api/dealership"
#         # Get dealers from the URL
#         dealerships = get_dealers_from_cf(url)
#         # Concat all dealer's short name
#         dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
#         # Return a list of dealer short name
#         return HttpResponse(dealer_names)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request, dealer_id):
    context = {}
    url = f"https://586dc592.us-south.apigw.appdomain.cloud/api/review?dealerId={dealer_id}"
    reviews_obj = get_dealer_reviews_from_cf(url, dealer_id)
    # reviews = ' '.join(["Review : " + review.review + " => sentiment : " +
    #                    review.sentiment + "<br>" for review in reviews_obj])
    context["reviews_list"] = reviews_obj
    context["dealerId"] = dealer_id

    return render(request, 'djangoapp/dealer_details.html', context)


# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
def add_review(request, dealerId):
    url = "https://586dc592.us-south.apigw.appdomain.cloud/api/review"

    context = {}
    context["dealerId"] = dealerId

    if request.method == 'GET':
        context["CarModel"] = CarModel.objects.filter(id=dealerId)
        return render(request, 'djangoapp/add_review.html', context=context)
    if request.method == 'POST':
        json_payload = dict()
        review = dict()
        review["id"] = dealerId
        review["review"] = request.POST["content"]
        car = request.POST["car"]
        model = car.split("-")[0]
        make = car.split("-")[1]
        year = car.split("-")[2]
        review["car_model"] = model
        review["car_make"] = make
        review["car_year"] = year
        review["purchase"] = request.POST["purchasecheck"]
        review["purchase_date"] = request.POST["purchasedate"]
        review["review_time"] = datetime.utcnow().isoformat()

        json_payload["review"] = review
        response = post_request(url, review, dealerId=dealerId)

        return redirect("djangoapp:dealer_details", dealerId=dealerId)
