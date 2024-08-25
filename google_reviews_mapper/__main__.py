"""Main module for downloading Maps data and exporting in a clean format."""

import os
import datetime
import dotenv
import google_reviews_mapper.compile_restaurants
import google_reviews_mapper.get_restaurants
import google_reviews_mapper.transform.tools

dotenv.load_dotenv()

API_KEY = os.getenv("GMAPS_API_KEY")
LOCATION = "40.7606586, -111.8927191"
RADIUS = 500
ITERATIONS = 10
RAW_OUTPUT_ROOT = "./output/data"
RAW_OUTPUT_DIR = (
    f"{RAW_OUTPUT_ROOT}/{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')}"
)
CLEAN_OUTPUT_DIR = (
    f"./output/clean/{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')}"
)

if __name__ == "__main__":
    google_reviews_mapper.get_restaurants.download_data(
        API_KEY,
        LOCATION,
        RADIUS,
        ITERATIONS,
        RAW_OUTPUT_DIR,
        city_county="county",
        map_only=True,
    )

    google_reviews_mapper.compile_restaurants.output_results(
        input_dir=RAW_OUTPUT_ROOT, output_dir=CLEAN_OUTPUT_DIR, include_plots=False
    )
