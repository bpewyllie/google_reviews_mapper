"""
Functions to retrieve restaurants from Google Maps APIs.
"""

import time
import json
import requests


def get_restaurants_around_location_new(
    api_key: str, location: str, radius: int
) -> list:
    """
    Uses the Nearby Search (New) API to retrieve a list of up to 20 restaurants centered around a
    location defined by latitude, longtiude coordinates and a given radius in meters.

    :param str api_key: Google Maps API Key
    :param str location: (latitude, longtiude) tuple formatted as string
    :param int radius: distance in meters to search around the location
    :rtype: list
    :return: list of restaurant jsons
    """
    url = "https://places.googleapis.com/v1/places:searchNearby"

    # fields to include
    field_mask = [
        "places.id",
        "places.displayName.text",
        "places.rating",
        "places.userRatingCount",
        "places.shortFormattedAddress",
        "places.priceLevel",
        # 0: free, 1: inexpensive, 2: moderate, 3: expensive, 4: very expensive
        "places.location",
        "places.primaryType",
        "places.primaryTypeDisplayName.text",
        "places.types",
        # "places.regularOpeningHours.weekdayDescriptions"
    ]

    # define the headers
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": f"{api_key}",
        "X-Goog-FieldMask": ",".join(field_mask),
    }

    # primary types to include
    included_types = [
        "american_restaurant",
        "bakery",
        "bar",
        "barbecue_restaurant",
        "brazilian_restaurant",
        "breakfast_restaurant",
        "brunch_restaurant",
        "cafe",
        "chinese_restaurant",
        "coffee_shop",
        "fast_food_restaurant",
        "french_restaurant",
        "greek_restaurant",
        "hamburger_restaurant",
        "ice_cream_shop",
        "indian_restaurant",
        "indonesian_restaurant",
        "italian_restaurant",
        "japanese_restaurant",
        "korean_restaurant",
        "lebanese_restaurant",
        "meal_delivery",
        "meal_takeaway",
        "mediterranean_restaurant",
        "mexican_restaurant",
        "middle_eastern_restaurant",
        "pizza_restaurant",
        "ramen_restaurant",
        "restaurant",
        "sandwich_shop",
        "seafood_restaurant",
        "spanish_restaurant",
        "steak_house",
        "sushi_restaurant",
        "thai_restaurant",
        "turkish_restaurant",
        "vegan_restaurant",
        "vegetarian_restaurant",
        "vietnamese_restaurant",
    ]

    # define the request body
    body = {
        "includedPrimaryTypes": included_types,
        "rankPreference": "DISTANCE",
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": float(location.split(", ")[0]),
                    "longitude": float(location.split(", ")[1]),
                },
                "radius": radius,
            }
        },
    }

    # make the POST request
    response = requests.post(url, headers=headers, json=body)
    res_json = json.loads(response.text)
    results = res_json.get("places", [])

    return results


# example usage
# res = get_restaurants_around_location_new("40.7606586, -111.8927191", 500)
# res[0]


def get_restaurants_around_location(
    api_key: str, location: str, radius: int = None
) -> list:
    """
    Uses the Nearby Search API to retrieve a list of up to 60 restaurants centered around a
    location defined by latitude, longtiude coordinates and a given radius in meters.

    :param str api_key: Google Maps API Key
    :param str location: (latitude, longtiude) tuple formatted as string
    :param int radius: distance in meters to search around the location
    :rtype: list
    :return: list of restaurant jsons
    """
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

    params = {
        "location": location,  # center to search around
        "radius": f"{radius}",  # meters
        "keyword": "restaurant",
        "rankby": "distance",
        "key": f"{api_key}",
    }

    response = requests.get(url, params=params)
    res_json = json.loads(response.text)
    results = res_json["results"]
    page_token = res_json["next_page_token"]

    # get next page of results using page token
    while page_token:
        print(page_token)

        params = {"pagetoken": page_token, "key": f"{api_key}"}

        time.sleep(3)  # wait for token to be usable in request
        response = requests.get(url, params=params)
        results.extend(json.loads(response.text)["results"])

        if "next_page_token" in json.loads(response.text).keys():
            page_token = json.loads(response.text)["next_page_token"]

        else:
            page_token = None

    return results
