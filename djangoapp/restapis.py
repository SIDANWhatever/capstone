import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))


def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))

    try:
        # if kwargs['apikey']:
        #     # Basic authentication GET
        #     api_key = kwargs['apikey']
        #     response = requests.get(url, params=kwargs, headers={'Content-Type': 'application/json'},
        #                             auth=HTTPBasicAuth('apikey', api_key))
        # else:
        #     # no authentication GET
        response = requests.get(url, headers={'Content-Type': 'application/json'},
                                params=kwargs)
        # Call get method of requests library with URL and parameters
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)


def post_request(url, json_payload, **kwargs):
    response = requests.post(url, params=kwargs, json=json_payload)
    return response

# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list


def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["All Dealers"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list


def get_dealer_reviews_from_cf(url, dealerId):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["All Dealers"]["docs"]
        for dealer in dealers:
            dealer_doc = dealer
            print(dealer)
            if int(dealer_doc["dealership"]) == dealerId:
                sentiment = analyze_review_sentiments(dealer_doc["review"])
                # sentiment = "ok"
                if dealer_doc["purchase"]:
                    review_obj = DealerReview(
                        dealership=dealer_doc["dealership"],
                        name=dealer_doc["name"],
                        purchase=dealer_doc["purchase"],
                        review=dealer_doc["review"],
                        purchase_date=dealer_doc["purchase_date"],
                        car_make=dealer_doc["car_make"],
                        car_model=dealer_doc["car_model"],
                        id=dealer_doc["id"],
                        car_year=dealer_doc["car_year"],
                        sentiment=sentiment
                    )
                else:
                    review_obj = DealerReview(
                        dealership=dealer_doc["dealership"],
                        name=dealer_doc["name"],
                        purchase=dealer_doc["purchase"],
                        review=dealer_doc["review"],
                        id=dealer_doc["id"],
                        sentiment=sentiment
                    )

                results.append(review_obj)

    return results


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
# def analyze_review_sentiments(dealerreview, **kwargs):
#     api_key = "F0V0MYMsv164-ibNzcunQi54tq6csUnqx6ghvZt5bktK"
#     url = "https://api.eu-gb.natural-language-understanding.watson.cloud.ibm.com/instances/fb87c486-f6a7-4195-b573-83a325e4af55"

#     params = dict()
#     params["text"] = kwargs["text"]
#     params["version"] = kwargs["version"]
#     params["features"] = kwargs["features"]
#     params["return_analyzed_text"] = kwargs["return_analyzed_text"]
#     response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                             auth=HTTPBasicAuth('apikey', api_key))
#     return response


def analyze_review_sentiments(dealerreview):
    apikey = "F0V0MYMsv164-ibNzcunQi54tq6csUnqx6ghvZt5bktK"
    url_key = "https://api.eu-gb.natural-language-understanding.watson.cloud.ibm.com/instances/fb87c486-f6a7-4195-b573-83a325e4af55"

    authenticator = IAMAuthenticator(apikey)
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2021-08-01',
        authenticator=authenticator
    )

    natural_language_understanding.set_service_url(url_key)

    response = natural_language_understanding.analyze(
        text=dealerreview,
        features=Features(sentiment=SentimentOptions())).get_result()

    return response["sentiment"]["document"]["label"]
