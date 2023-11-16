from datetime import date
from functools import lru_cache

import folium
import geopandas as gpd
import numpy as np
import pandas as pd
from streamlit_folium import st_folium


"""""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """""
    Services for getting/processing Nominatim country boundary data from OSM
"""""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """""
# Source: https://gist.github.com/adrianespejo/5df28ce987db64ba753619502ee3d812

def create_nominatim_search_url(
    country_code: str
) -> str:
    """
    Function to fetch OSM Search URL using Nominatim Search API

    Parameters
    ----------
        query: str - takes the string as name of country/region/city/settlement

    Returns
        search_url: str - url of the nominatim query result
    -------
    """
    NOMINATIM_SEARCH_ENDPOINT = "https://nominatim.openstreetmap.org/search"
    
    params: dict = {
        "addresstype": "country",
        "namedetails": 1,
        "polygon_geojson": 1,
        "hierarchy": 1,
    }

    params_query = "&".join(
        f"{param_name}={param_value}" for param_name, param_value in params.items()
    )

    search_url = f"{NOMINATIM_SEARCH_ENDPOINT}?q={country_code}&featureType=country&{params_query}&format=geojson"

    return search_url


def convert_nominatim_search_url_to_gdf(
    nominatim_search_url: str,
) -> gpd.GeoDataFrame:
    """
    Function to convert nominatim queried url to geodataframe

    Parameters:
    ----------
        nominatim_search_url: str - url of the nominatim query result

    Returns:
    -------
        gdf: geodataframe - geodataframe of the query result
    """

    gdf = gpd.read_file(nominatim_search_url)

    gdf = gdf.to_crs(epsg=4326)

    gdf_centroid = gdf.to_crs("+proj=cea").centroid.to_crs(gdf.crs)
    gdf_centroid = gdf_centroid.total_bounds
    # print(gdf_centroid, "\n")

    center_x = (gdf_centroid[0] + gdf_centroid[2]) / 2  # Average of minx and maxx
    center_y = (gdf_centroid[1] + gdf_centroid[3]) / 2  # Average of miny and maxy
    center_coors = [center_y, center_x]

    return gdf, center_coors


def display_osm_boundary(gdf: gpd.GeoDataFrame, centroid: np.ndarray) -> st_folium:
    """
    Function to display the map of the geodataframe

    Parameters:
    ----------
        gdf: geodataframe - geodataframe of the query result
        centroid: narray - array of the coordinates of the centroid of the geodataframe

    Returns:
    -------
        st_map: streamlit-folium map - map of the geodataframe
    """

    foliumMap = folium.Map(location=centroid, zoom_start=4, tiles="CartoDB positron")

    # add the country boundary to the map
    for _, r in gdf.iterrows():
        # without simplifying the representation of each borough, the map might not be displayed
        # sim_geo = gpd.GeoSeries(r['geometry'])
        sim_geo = gpd.GeoSeries(r["geometry"]).simplify(tolerance=0.001)
        geo_j = sim_geo.to_json()
        geo_j = folium.GeoJson(
            data=geo_j, style_function=lambda x: {"fillColor": "orange"}
        )
        geo_j.add_to(foliumMap)

    st_map = st_folium(foliumMap, width=800, height=500)

    print("Map displayed successfully!")

    return st_map
