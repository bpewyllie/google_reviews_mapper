"""Main module for downloading Maps data and exporting in a clean format."""

import os
import datetime
import dotenv
import google_reviews_mapper.get_restaurants

dotenv.load_dotenv()

API_KEY = os.getenv("GMAPS_API_KEY")
LOCATION = "40.7606586, -111.8927191"
RADIUS = 500
ITERATIONS = 10
OUTPUT_DIR = f"./output/data/{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')}"

if __name__ == "__main__":
    google_reviews_mapper.get_restaurants.download_data(
        API_KEY,
        LOCATION,
        RADIUS,
        ITERATIONS,
        OUTPUT_DIR,
        city_county="county",
        map_only=True,
    )
