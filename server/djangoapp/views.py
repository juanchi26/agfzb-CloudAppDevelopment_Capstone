from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
# from .restapis import related methods
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
from .restapis import get_dealer_reviews_from_cf, post_request, get_dealers_from_cf, get_dealer_by_id_from_cf
from .models import CarDealer, CarMake, CarModel, DealerReview
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

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
        return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return redirect('djangoapp:index')
    else:
        return redirect('djangoapp:index')


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    print("Log out the user `{}`".format(request.user.username))
    logout(user)
    return redirect('djangoapp:index')


# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        # print("here!!!")
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.debug("{} is new user".format(request.username))

        if not user_exist:
            user = User.objects.create_user(
                username=username, 
                password=password, 
                last_name=lastname, 
                first_name=firstname
            )
            # log in the user
            login(request, user)
            return redirect('djangoapp:index')
        else:
            return render(request, 'djangoapp:registration', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://us-east.functions.appdomain.cloud/api/v1/web/coursera-1c4_coursera-us-east/dealership-package/dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        context['dealership_list'] = dealerships
        # Return a list of dealer short name
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    context = {}
    dealerships = get_dealer_by_id_from_cf(
        url="https://us-east.functions.appdomain.cloud/api/v1/web/coursera-1c4_coursera-us-east/dealership-package/dealership", 
        dealerId=dealer_id
    )
    context["dealer_name"] = dealerships[0].name
    context["dealer_id"] = dealer_id

    url = "https://us-east.functions.appdomain.cloud/api/v1/web/coursera-1c4_coursera-us-east/dealership-package/review"
    reviews = get_dealer_reviews_from_cf(url, dealer_id)
    context['review_list'] = reviews
    return render(request, 'djangoapp/dealer_details.html', context) # also sentiment?

    
# Create a `add_review` view to submit a review
def add_review(request, dealer_id):    
    context = {}    
    url = "https://eu-gb.functions.appdomain.cloud/api/v1/web/coursera-1c4_capstone-eu/dealership-package/post-review.json"
    
    if not request.user.is_authenticated:
        redirect('djangoapp/registration.html')
    else:
        if request.method == "POST":
            review = dict()
            review["time"] = datetime.utcnow().isoformat()
            review["dealership"] = dealer_id
            review["name"] = username
            review["review"] = request.POST["content"]
            review["purchase"] = False
            if "purchasecheck" in request.POST:
                if request.POST["purchasecheck"] == 'on':
                    review["purchase"] = True
            review["purchase_date"] = request.POST["purchasedate"]
            review["car_make"] = car.make.name
            review["car_model"] = car.name
            review["car_year"] = int(car.year.strftime("%Y"))
            
            json_payload = dict()
            json_payload["review"] = review
            response = post_request(url=post_url, payload=json_payload)
            print(response)
            return redirect("djangoapp:dealer_details", dealer_id)
        # this redirect will be routed to get_dealer_detailers() above
        elif request.method == "GET":
            cars = CarModel.objects.filter(dealer_id=dealer_id)
            print(cars)
            context["cars"] = cars
            return render(request, 'djangoapp/add_review.html', context)