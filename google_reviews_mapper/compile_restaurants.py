"""
Main module for compiling and outputting clean restaurant data from Google Maps.
"""

import datetime
import google_reviews_mapper.transform.tools


def output_results(input_dir: str, output_dir: str, include_plots: False) -> None:
    """
    Given a root directory of restaurant location files and an output directory,
    creates a ratings histogram and summary statistics text file of restaurant ratings.

    :param str input_dir: directory to read the input files from
    :param str output_dir: directory to save the output files to
    :param bool include_plots: whether to save plots or not
    :rtype: None
    """

    input_dir = "./output/data"
    output_dir = f"./output/clean/{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')}"
    plot_file = f"{output_dir}/ratings_histogram.png"
    summary_stats_file = f"{output_dir}/summary_stats.txt"

    gdf = google_reviews_mapper.transform.tools.clean_restaurant_data(
        input_dir, output_dir
    )
    print(f"Restaurant data saved to {output_dir}/locs_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')}.csv")
    google_reviews_mapper.transform.tools.get_summary_stats(gdf, summary_stats_file)
    print(f"Restaurant summary stats saved to {summary_stats_file}")
    
    if include_plots:
        google_reviews_mapper.transform.tools. plot_ratings_distribution(gdf, plot_file)
        print(f"Restaurant ratings histogram saved to {plot_file}")
