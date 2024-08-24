"""
Functions to work with GPS coordinates.
"""

import math
import gmplot
import geopandas
import matplotlib.pyplot
import pandas
import shapely.geometry


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

    return list(set(locs))


def filter_grid_by_region(
    locations: list, region_gdf: geopandas.GeoDataFrame
) -> geopandas.GeoDataFrame:
    """
    Given a starting grid of locations, returns a subset that are fully contained by the region(s) defined by a provided GeoDataFrame.

    :param list locations: list of locations, where each location is a string of latitude, longitude
    :param geopandas.GeoDataFrame region_gdf: GeoDataFrame with a geometry field for defining the shape(s) of the region(s)
    :rtype: geopandas.GeoDataFrame
    :return: GeoDataFrame of the subset of locations
    """

    # Convert the list of locations to Point objects
    points = [
        shapely.geometry.Point(float(loc.split(", ")[1]), float(loc.split(", ")[0]))
        for loc in locations
    ]

    # Create a GeoDataFrame from the Point objects
    locations_gdf = geopandas.GeoDataFrame(geometry=points)

    # Get locations within SLCo boundaries
    gdfs_within_boundaries = []

    for _, boundary in region_gdf.iterrows():
        points_within = locations_gdf[locations_gdf.within(boundary.geometry)]
        gdfs_within_boundaries.append(points_within)

    filtered_points_gdf = pandas.concat(gdfs_within_boundaries)

    return filtered_points_gdf


def map_grid_locs_static(
    locations_gdf: geopandas.GeoDataFrame, region_gdf: geopandas.GeoDataFrame, title: str, file: str
) -> None:
    """
    Creates and saves a static map of grid locations and region(s).

    :param geopandas.GeoDataFrame locations_gdf: GeoDataFrame of locations to plot
    :param geopandas.GeoDataFrame region_gdf: GeoDataFrame of boundary region(s) to plot
    :param str title: title of the plot
    :param str file: filename of the plot saved file
    :rtype: None
    """

    region_gdf.plot(color='lightgrey', edgecolor='black', figsize=(10, 10))
    locations_gdf.plot(ax=matplotlib.pyplot.gca(), color='red', markersize=5)

    # Annotate each polygon with its name
    for x, y, label in zip(region_gdf.to_crs('+proj=cea').geometry.centroid.x, region_gdf.to_crs('+proj=cea').geometry.centroid.y, region_gdf.NAME):
        matplotlib.pyplot.text(x, y, label, fontsize=8, ha='center', va='center')

    # Set the title
    matplotlib.pyplot.title('Municipal Boundaries and Points')
    
    # Save the plot
    matplotlib.pyplot.savefig(file)


def map_grid_locs_html(
    start_loc: str, distance: int, iterations: int, file: str
) -> None:
    """
    Creates and saves an interactive HTML map of grid locations given a starting location, distance, and
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
