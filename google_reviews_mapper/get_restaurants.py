"""
Main module for downloading restaurant data from Google Maps.
"""

import datetime
import os
import typing
import pandas
import geopandas
import google_reviews_mapper.gmaps.restaurants
import google_reviews_mapper.gps.tools


def download_data(
    api_key,
    start_location,
    radius,
    iterations,
    output_dir,
    city_county: typing.Literal["city", "county"] = "county",
    map_only: bool = False,
) -> None:
    """
    Given a Google Maps API Key, starting location, radius, and number of iterations,
    downloads a list of restaurants in an area.

    :param str api_key: Google Maps API Key
    :param str start_location: starting location (latitude, longtiude) tuple formatted as string
    :param int radius: number of meters to space grid points by
    :param int iterations: number of times to expand the grid away from the start_location
    :param str output_dir: directory to save the output files
        (map of search grid and restaurant list) to
    :param bool map_only: if True, do not generate the restaurant data, just the search grid map
    :rtype: None
    """

    if city_county not in ["city", "county"]:
        raise AttributeError("city_county arg must be either 'city' or 'county'")

    print(f"preparing directory for output at {output_dir}...")
    # Make directory for output
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    print("generating grid of locations...")
    locations = google_reviews_mapper.gps.tools.generate_grid_locs(
        start_location, radius, iterations
    )
    print(f"\n{len(locations)} gridpoints generated\n")

    print("filtering to region...")

    if city_county == "county":

        county_gdf = geopandas.read_file(
            "https://slco.org/slcogis/rest/services/Administration/MapServer/3/query?outFields=*&where=1%3D1&f=geojson"
        ).to_crs(epsg=4326)
        filtered_locs = google_reviews_mapper.gps.tools.filter_grid_by_region(
            locations, county_gdf
        )
        print(f"\n{len(filtered_locs)} gridpoints within county found\n")

        google_reviews_mapper.gps.tools.map_grid_locs_static(
            filtered_locs,
            county_gdf,
            "SL County Locations",
            f"{output_dir}/grid_{datetime.date.today().strftime('%Y-%m-%d-%H-%M')}.pdf",
        )

    if city_county == "city":

        city_gdf = county_gdf.loc[county_gdf["NAME"] == "SALT LAKE"]
        filtered_locs = google_reviews_mapper.gps.tools.filter_grid_by_region(
            locations, city_gdf
        )
        print(f"\n{len(filtered_locs)} gridpoints within county found\n")

        google_reviews_mapper.gps.tools.map_grid_locs_static(
            filtered_locs,
            city_gdf,
            "SLC Locations",
            f"{output_dir}/grid_{datetime.date.today().strftime('%Y-%m-%d-%H-%M')}.pdf",
        )

    if map_only:
        return

    print("grabbing data from Maps API...")
    results = []
    filtered_locs_list = [f"{point.y}, {point.x}" for point in filtered_locs.geometry]

    # Get nearest <=60 restaurants centered around each location
    i = 0
    for location in filtered_locs_list:
        i += 1
        print(
            f"\nretrieving locations around gridpoint {i} of {len(filtered_locs_list)}",
            end="\r",
        )
        results.extend(
            google_reviews_mapper.gmaps.restaurants.get_restaurants_around_location(
                api_key, location
            )
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
        f"{output_dir}/locs_{datetime.date.today().strftime('%Y-%m-%d-%H-%M')}.csv",
        index=False,
    )
