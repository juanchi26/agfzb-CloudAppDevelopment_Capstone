import requests
import json
# import related models here
from .models import CarDealer
from requests.auth import HTTPBasicAuth
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions
from .models import CarDealer, CarMake, CarModel, DealerReview
import time

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {}".format(url))
    print("kwawgs ")
    print(kwargs)
    response = requests.get(
        url, 
        headers={'Content-Type': 'application/json'},
        params=kwargs,
    )
    print(response)
 
    # print("Network exception occured")
    status_code = response.status_code
    print("With status {}".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, payload, **kwargs):
    print(kwargs)
    status_code = 0
    print("POST to {}".formate(url))
    response = requests.post(url, params=kwargs, json=payload)
    # print("Network exception occured")
    status_code = response.status_code
    print("With status {}".format(status_code))
    json_data = json.lodas(response.text)
    return json_data


# Create a get_dealers_from_cf method to get dealers from a cloud function
def get_dealers_from_cf(url, **kwargs):
    # - Call get_request() with specified arguments
    # - Parse JSON results into a CarDealer object list
    results = []
    json_result = get_request(url)
    if json_result:
        dealers = json_result
        for dealer_doc in dealers:
            dealer_doc = dealer_doc['doc']
            dealer_obj = CarDealer(
                address = dealer_doc["address"],
                city = dealer_doc["city"],
                name = dealer_doc["full_name"],
                id_ = dealer_doc["id"],
                lat = dealer_doc["lat"], 
                long_ = dealer_doc["long"],
                short_name = dealer_doc["short_name"],
                st = dealer_doc["st"],
                zip_ = dealer_doc["zip"],
            )
            results.append(dealer_obj)
    return results

          
def get_dealer_by_id_from_cf(url, dealerId):
    results = []
    for dealer_obj in get_dealers_from_cf(url):
        if dealer_obj.id_ == dealerId:
            results.append(dealer_obj)
    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, dealer_Id):
    results = []
    json_result = get_request(url, dealer_id=dealer_Id)
    if json_result:
        reviews = json_result['data']['docs']
        
        for review in reviews:
            # dealer_doc = dealer
            # print("review", review, "\n")
            review_obj = DealerReview(
                dealership = review["dealership"],
                name = review["name"],
                purchase = review["purchase"],
                review = review["review"], 
            )

            if "id" in review:
                review_obj.id_ = review["id"]
            if "purchase_date" in review:
                review_obj.purchase_date = review["purchase_date"]
            if "car_make" in review:
                review_obj.car_make = review["car_make"]
            if "car_model" in review:
                review_obj.car_model = review["car_model"]
            if "car_year" in review:
                review_obj.car_year = review["car_year"]
          
            review_obj.sentiment = analyze_review_sentiments(review_obj.review)
            results.append(review_obj)
    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(text):
    params = dict()
    url = "https://api.au-syd.natural-language-understanding.watson.cloud.ibm.com/instances/e996d582-07d8-4a5c-8208-59321fc3e366"
    api_key = "s4oFoP_cLXoaGERiL6BPSIbTKsZ74Pm6CIhAppO6stK9"
    authenticator = IAMAuthenticator(api_key) 
    natural_language_understanding = NaturalLanguageUnderstandingV1(version='2021-08-01',authenticator=authenticator) 
    natural_language_understanding.set_service_url(url) 
    print("NLU text", text)
    text = text+"Hello Hello Hello"
    sentiment=SentimentOptions(targets=[text])
    response = natural_language_understanding.analyze(text=text, 
        features=Features(sentiment=sentiment)).get_result()
    label = json.dumps(response, indent=2)
    label = response['sentiment']['document']['label'] 
    return label
    
    
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative



