"""
Tools for transforming and mapping geo files.
"""

import datetime
import os
import geopandas
import matplotlib.pyplot as plt
import pandas
import shapely


def clean_restaurant_data(
    input_dir: str,
    output_dir: str,
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

    # Group restaurants with multiple locations
    gdf["chain_stars"] = gdf.groupby("name")["stars"].transform(lambda x: x.sum())
    gdf["chain_ratings_total"] = gdf.groupby("name")["user_ratings_total"].transform(
        lambda x: x.sum()
    )
    gdf["chain_wtd_avg_rating"] = gdf["chain_stars"] / gdf["chain_ratings_total"]
    gdf = gdf.loc[
        gdf["primary_type"].isin(
            ["restaurant", "meal_takeaway", "bakery", "cafe", "meal_delivery"]
        )
    ]

    # Identify locations in airport
    airport_loc = shapely.geometry.Point(-111.9768056, 40.8015768)
    gdf["in_airport"] = gdf["geometry"].apply(lambda x: x.distance(airport_loc) <= 0.02)

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


def plot_ratings_distribution(
    restaurants_gdf: geopandas.GeoDataFrame, file: str
) -> None:
    """
    Saves a histogram of the distribution of ratings for a given GeoDataFrame of
    restaurant review data.

    :param geopandas.GeoDataFrame restaurants_gdf: GeoDataFrame of restaurant review data
    :param str output_dir: filename of the plot saved file
    :rtype: None
    """

    # Create a histogram
    plt.hist(restaurants_gdf["rating"], bins=20, edgecolor="black")
    plt.xlabel("Rating")
    plt.ylabel("Frequency")
    plt.title("Distribution of Ratings")
    plt.grid(False)
    plt.savefig(file)


def get_summary_stats(restaurants_gdf: geopandas.GeoDataFrame, file: str) -> None:
    """
    Saves a file of some interesting summary statistics for a given GeoDataFrame
    of restaurant review data.

    :param geopandas.GeoDataFrame restaurants_gdf: GeoDataFrame of restaurant review data
    :param str output_dir: filename of the summary stats saved file
    :rtype: None
    """

    # Filter data to reasonable set
    gdf = restaurants_gdf.loc[~restaurants_gdf["in_airport"]]
    gdf100 = gdf.loc[gdf["user_ratings_total"] >= 100]
    gdf100 = gdf100.sort_values(by=["rating"], ascending=False)
    pop = gdf100.sort_values(by=["user_ratings_total"], ascending=False)

    # Define chain restaurant as anything with 3+ locations in sample
    chains = gdf.loc[gdf["n_locations"] >= 3]
    chains = chains.drop_duplicates("name")
    chains = chains.sort_values(by=["chain_wtd_avg_rating"], ascending=False)

    with open(
        "./google_reviews_mapper/transform/stats_template.txt", "r", encoding="utf-8"
    ) as f:
        text = f.read()

    text = text.format(
        date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        n_obs=len(gdf),
        n_obs_100=len(gdf100),
        mean_rating=gdf100.rating.mean().round(0),
        min_rating=gdf100.rating.min(),
        first_qtile=gdf100.rating.quantile(0.25),
        median=gdf100.rating.quantile(0.5),
        third_qtile=gdf100.rating.quantile(0.75),
        max_rating=gdf100.rating.max(),
        top_1=f"{gdf100['name'].iloc[0]} - {gdf100['vicinity'].iloc[0]} ({gdf100['rating'].iloc[0]}, {int(gdf100['user_ratings_total'].iloc[0])})",
        top_2=f"{gdf100['name'].iloc[1]} - {gdf100['vicinity'].iloc[1]} ({gdf100['rating'].iloc[1]}, {int(gdf100['user_ratings_total'].iloc[1])})",
        top_3=f"{gdf100['name'].iloc[2]} - {gdf100['vicinity'].iloc[2]} ({gdf100['rating'].iloc[2]}, {int(gdf100['user_ratings_total'].iloc[2])})",
        top_4=f"{gdf100['name'].iloc[3]} - {gdf100['vicinity'].iloc[3]} ({gdf100['rating'].iloc[3]}, {int(gdf100['user_ratings_total'].iloc[3])})",
        top_5=f"{gdf100['name'].iloc[4]} - {gdf100['vicinity'].iloc[4]} ({gdf100['rating'].iloc[4]}, {int(gdf100['user_ratings_total'].iloc[4])})",
        bot_1=f"{gdf100['name'].iloc[-1]} - {gdf100['vicinity'].iloc[-1]} ({gdf100['rating'].iloc[-1]}, {int(gdf100['user_ratings_total'].iloc[-1])})",
        bot_2=f"{gdf100['name'].iloc[-2]} - {gdf100['vicinity'].iloc[-2]} ({gdf100['rating'].iloc[-2]}, {int(gdf100['user_ratings_total'].iloc[-2])})",
        bot_3=f"{gdf100['name'].iloc[-3]} - {gdf100['vicinity'].iloc[-3]} ({gdf100['rating'].iloc[-3]}, {int(gdf100['user_ratings_total'].iloc[-3])})",
        bot_4=f"{gdf100['name'].iloc[-4]} - {gdf100['vicinity'].iloc[-4]} ({gdf100['rating'].iloc[-4]}, {int(gdf100['user_ratings_total'].iloc[-4])})",
        bot_5=f"{gdf100['name'].iloc[-5]} - {gdf100['vicinity'].iloc[-5]} ({gdf100['rating'].iloc[-5]}, {int(gdf100['user_ratings_total'].iloc[-5])})",
        pop_1=f"{pop['name'].iloc[0]} - {pop['vicinity'].iloc[0]} ({pop['rating'].iloc[0]}, {int(pop['user_ratings_total'].iloc[0])})",
        pop_2=f"{pop['name'].iloc[1]} - {pop['vicinity'].iloc[1]} ({pop['rating'].iloc[1]}, {int(pop['user_ratings_total'].iloc[1])})",
        pop_3=f"{pop['name'].iloc[2]} - {pop['vicinity'].iloc[2]} ({pop['rating'].iloc[2]}, {int(pop['user_ratings_total'].iloc[2])})",
        pop_4=f"{pop['name'].iloc[3]} - {pop['vicinity'].iloc[3]} ({pop['rating'].iloc[3]}, {int(pop['user_ratings_total'].iloc[3])})",
        pop_5=f"{pop['name'].iloc[4]} - {pop['vicinity'].iloc[4]} ({pop['rating'].iloc[4]}, {int(pop['user_ratings_total'].iloc[4])})",
        top_chain_1=f"{chains['name'].iloc[0]} ({round(chains['chain_wtd_avg_rating'].iloc[0], 1)}, {int(chains['chain_ratings_total'].iloc[0])})",
        top_chain_2=f"{chains['name'].iloc[1]} ({round(chains['chain_wtd_avg_rating'].iloc[1], 1)}, {int(chains['chain_ratings_total'].iloc[1])})",
        top_chain_3=f"{chains['name'].iloc[2]} ({round(chains['chain_wtd_avg_rating'].iloc[2], 1)}, {int(chains['chain_ratings_total'].iloc[2])})",
        top_chain_4=f"{chains['name'].iloc[3]} ({round(chains['chain_wtd_avg_rating'].iloc[3], 1)}, {int(chains['chain_ratings_total'].iloc[3])})",
        top_chain_5=f"{chains['name'].iloc[4]} ({round(chains['chain_wtd_avg_rating'].iloc[4], 1)}, {int(chains['chain_ratings_total'].iloc[4])})",
        bot_chain_1=f"{chains['name'].iloc[-1]} ({round(chains['chain_wtd_avg_rating'].iloc[-1], 1)}, {int(chains['chain_ratings_total'].iloc[-1])})",
        bot_chain_2=f"{chains['name'].iloc[-2]} ({round(chains['chain_wtd_avg_rating'].iloc[-2], 1)}, {int(chains['chain_ratings_total'].iloc[-2])})",
        bot_chain_3=f"{chains['name'].iloc[-3]} ({round(chains['chain_wtd_avg_rating'].iloc[-3], 1)}, {int(chains['chain_ratings_total'].iloc[-3])})",
        bot_chain_4=f"{chains['name'].iloc[-4]} ({round(chains['chain_wtd_avg_rating'].iloc[-4], 1)}, {int(chains['chain_ratings_total'].iloc[-4])})",
        bot_chain_5=f"{chains['name'].iloc[-5]} ({round(chains['chain_wtd_avg_rating'].iloc[-5], 1)}, {int(chains['chain_ratings_total'].iloc[-5])})",
    )

    with open(f"{file}", "w", encoding="utf-8") as f:
        f.write(text)


def __enter__():
    """
    Helper function for running the tools module from poetry
    """

    input_dir = "./output/data"
    output_dir = f"./output/clean/{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')}"
    plot_file = f"{output_dir}/plot.png"
    summary_stats_file = f"{output_dir}/summary_stats.txt"

    gdf = clean_restaurant_data(input_dir, output_dir)
    get_summary_stats(gdf, summary_stats_file)
    plot_ratings_distribution(gdf, plot_file)
