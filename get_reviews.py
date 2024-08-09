"""
Scripts to retrieve restaurant review data in a region.
"""

import json
import math
import time
from datetime import date
import gmplot
import requests
import pandas


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
        "key": "AIzaSyCOU9BGhHu2Vv58uTMTinh1AOdqUziy2bs",
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


def add_to_latitude(start_lat: float, meters_diff: int) -> float:
    """
    Given a starting latiude coordinate and a number of meters to add,
    calculates the resulting latitude.

    :param float start_lat: starting latitude as a float
    :param int meters_diff: number of meters (as an int) to add to the start_lat
    :rtype: float
    :return: new latitude
    """
    km_diff = meters_diff / 1000
    new_lat = start_lat + (km_diff / 6378) * (180 / math.pi)

    return new_lat


def add_to_longitude(start_lon: float, start_lat: float, meters_diff: int) -> float:
    """
    Given a starting latitude, longitude coordinate pair and a number of meters to add,
    calculates the resulting longitude.

    :param float start_lat: starting latitude as a float
    :param float start_lon: starting longitude as a float
    :param int meters_diff: number of meters (as an int) to add to the start_lon
    :rtype: float
    :return: new longitude
    """
    km_diff = meters_diff / 1000
    new_lon = start_lon + (km_diff / 6378) * (180 / math.pi) / math.cos(
        start_lat * math.pi / 180
    )

    return new_lon


def generate_grid_locs(start_loc: str, distance: int, iterations: int) -> list:
    """
    Given a starting location defined by latitude and longitude, a distance to separate points by,
    and a number of iterations, generates a grid of locations centered around the starting location.

    :param str start_loc: starting latitude and longitude as a string
    :param int distance: number of meters to separate each nearest point from each other
    :param int iterations: number of times to search outward from the starting location
    :rtype: list
    :return: list of grid locations
    """
    start_lat, start_lon = map(float, start_loc.split(", "))
    locs = [start_loc]

    for i in range(-iterations, iterations + 1):
        for j in range(-iterations, iterations + 1):
            lat = add_to_latitude(start_lat, i * distance)
            lon = add_to_longitude(start_lon, start_lat, j * distance)
            loc = f"{lat}, {lon}"
            locs.append(loc)

    return locs


def map_grid_locs(start_loc: str, distance: int, iterations: int, file: str) -> None:
    """
    Creates and saves an HTML map of grid locations given a starting location, distance, and
    number of iterations.

    :param str start_loc: starting latitude and longitude as a string
    :param int distance: number of meters to separate each nearest point from each other
    :param int iterations: number of times to search outward from the starting location
    :param str file: file name and location to save to; should end in .html
    :rtype: None
    """

    # Compile full list of locations based on number of iterations
    locations = generate_grid_locs(start_loc, distance, iterations)

    # Extract latitudes and longitudes from locs
    latitudes = [float(loc.split(", ")[0]) for loc in locations]
    longitudes = [float(loc.split(", ")[1]) for loc in locations]

    # Create a gmplot object centered around the start location
    gmap = gmplot.GoogleMapPlotter(latitudes[0], longitudes[0], iterations)

    # Scatter plot the locations
    gmap.scatter(latitudes, longitudes, "#3B0B39", size=40, marker=False)

    # Draw the map and save it as an HTML file
    gmap.draw(f"{file}")


# Example usage
# map_grid_locs("40.7606586, -111.8927191", 550, 5, "my-grid.html")

## Full example
# Start at rough center of SLC (400 S and Main)
# start_lat = 40.7606586
# start_lon = -111.8927191
# start_loc = str(start_lat) + ", " + str(start_lon)

# # Distance between grid locations in meters
# distance = 500

# # Number of iterations in each direction from start location
# iterations = 13

# # Compile full list of locations based on number of iterations
# locations = generate_grid_locs(start_loc, distance, iterations)

# results = []

# # Get nearest 60 restaurants centered around each location
# for location in locations:
#   results.extend(get_restaurants_around_location(api_key=API_KEY, location, distance))

# # Extract nested JSON elements
# for result in results:
#   lat = result['geometry']['location']['lat']
#   lng = result['geometry']['location']['lng']
#   result['latitude'] = lat
#   result['longitude'] = lng
#   result['types_str'] = ",".join(result['types'])

# Store in dataframe
# all_restaurants = pandas.DataFrame.from_records(results)[["name", "rating", "user_ratings_total", "vicinity", "price_level", "latitude", "longitude", "types_str"]].drop_duplicates()

# Save as CSV
# file_path = f'/myfile_{date.today().strftime("%Y-%m-%d")}.csv'
# all_restaurants.to_csv(file_path, index=False)
