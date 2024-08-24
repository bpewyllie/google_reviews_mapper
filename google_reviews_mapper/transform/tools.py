"""
Tools for transforming and mapping geo files.
"""

import datetime
import os
import geopandas
import pandas
import shapely


def clean_restaurant_data(
    input_dir: str = "./output/data",
    output_dir: str = f"./output/clean/{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')}",
) -> None | geopandas.GeoDataFrame:
    """
    Reads CSV files located at input_dir, merges into a single GeoDataFrame, and saves to output_dir

    :param str input_dir: directory to read the input files from
    :param str output_dir: directory to save the output files to; if None, the GDF is returned only
    :rtype: (None | geopandas.GeoDataFrame)
    :return: cleaned GeoDataFrame, if specified
    """
    dfs_list = []

    # Get all CSV files
    for path, subdirs, files in os.walk(input_dir):
        for name in files:
            if name.endswith("csv"):
                df = pandas.read_csv(os.path.join(path, name))
                df["file_name"] = name
                dfs_list.append(df)

    # Merge data, convert to Geo DataFrame
    all_data = pandas.concat(dfs_list, ignore_index=True)
    gdf = geopandas.GeoDataFrame(
        all_data,
        geometry=geopandas.points_from_xy(all_data.longitude, all_data.latitude),
        crs="EPSG:4326",
    )

    # Round the coordinates to 5 decimals and remove dupes
    gdf.geometry = shapely.set_precision(gdf.geometry, grid_size=0.001)
    gdf.drop_duplicates(["name", "geometry"], inplace=True)

    # Additional columns
    gdf["stars"] = gdf["rating"] * gdf["user_ratings_total"]
    gdf["primary_type"] = gdf["types_str"].apply(lambda x: x.split(",")[0])
    gdf["n_locations"] = gdf.groupby("name")["name"].transform(lambda x: x.count())
    gdf = gdf.loc[gdf["primary_type"].isin(["restaurant", "meal_takeaway", "bakery", "bar", "cafe", "meal_delivery"])]

    if output_dir:
        # Make directory for output
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        # Save
        gdf.to_csv(
            f"{output_dir}/locs_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')}.csv",
            index=False,
        )

    return gdf
