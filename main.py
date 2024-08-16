"""
Main module for executing the google reviews mapper from the command line.
"""

import datetime
import os
import pandas
import geopandas
import dotenv
import gmaps.restaurants
import gps.tools


dotenv.load_dotenv()

API_KEY = os.getenv("GMAPS_API_KEY")
LOCATION = "40.7606586, -111.8927191"
RADIUS = 500
ITERATIONS = 1
OUTPUT_DIR = f"./output/data/{datetime.date.today().strftime('%Y-%m-%d')}"


if __name__ == "__main__":

    print(f"preparing directory for output at {OUTPUT_DIR}...")
    # Make directory for output
    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)

    print("generating grid of locations...")
    locations = gps.tools.generate_grid_locs(LOCATION, RADIUS, ITERATIONS)
    
    print("filtering to SLC...")
    county_gdf = geopandas.read_file("https://slco.org/slcogis/rest/services/Administration/MapServer/3/query?outFields=*&where=1%3D1&f=geojson").to_crs(epsg=4326)
    city_gdf = county_gdf.loc[county_gdf["NAME"] == "SALT LAKE"]

    # county_locations = gps.tools.filter_grid_by_region(locations, county_gdf)
    city_locations = gps.tools.filter_grid_by_region(locations, city_gdf)
    # gps.tools.map_grid_locs_static(county_locations, county_gdf, "SL County Locations", f"{OUTPUT_DIR}/grid_{datetime.date.today().strftime('%Y-%m-%d')}.pdf")
    gps.tools.map_grid_locs_static(city_locations, city_gdf, "SLC Locations", f"{OUTPUT_DIR}/grid_{datetime.date.today().strftime('%Y-%m-%d')}.pdf")

    print("grabbing data from Maps API...")
    results = []
    city_locs = [f"{point.y}, {point.x}" for point in city_locations.geometry]
    # county_locs = [f"{point.y}, {point.x}" for point in county_locations.geometry]

    # Get nearest <=60 restaurants centered around each location
    for location in city_locs:
        results.extend(
            gmaps.restaurants.get_restaurants_around_location(API_KEY, LOCATION)
        )

    # Extract nested JSON elements
    for result in results:
        lat = result["geometry"]["location"]["lat"]
        lng = result["geometry"]["location"]["lng"]
        result["latitude"] = lat
        result["longitude"] = lng
        result["types_str"] = ",".join(result["types"])

    all_restaurants = pandas.DataFrame.from_records(results)[
        [
            "name",
            "rating",
            "user_ratings_total",
            "vicinity",
            "price_level",
            "latitude",
            "longitude",
            "types_str",
        ]
    ]
    all_restaurants.drop_duplicates(inplace=True)
    all_restaurants.to_csv(
        f"{OUTPUT_DIR}/locs_{datetime.date.today().strftime('%Y-%m-%d')}.csv",
        index=False,
    )
