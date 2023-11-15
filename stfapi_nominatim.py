import json
import requests
import streamlit as st

from services.nominatim_services import (
    convert_nominatim_search_url_to_gdf,
    get_gdf_centroid_coordinates,
    display_osm_boundary,
)


APP_TITLE = "FastAPI & Streamlit - Map App"


def set_state(i):
    st.session_state.stage = i


def osm_boundary_stmap():
    if "stage" not in st.session_state:
        st.session_state.stage = 0

    if st.session_state.stage >= 0:
        st.write(
            "From this list of country codes: https://wiki.openstreetmap.org/wiki/Nominatim/Country_Codes"
        )
        st.write(
            "Which country would you like to get the border boundaries from OSM for?"
        )

        entered_country_code = st.text_input(
            "Please enter the code of the country of interest from the list above",
            on_change=set_state,
            args=[1],
        )

    if st.session_state.stage >= 1:
        st.write(f'You entered: "{entered_country_code}"')

        inputs = {"country_code": entered_country_code}
        response_url = requests.post(
            "http://localhost:8000/fetch/nominatim_search_url",
            data=json.dumps(inputs),
        ).json()
        print(response_url)

        query_url = st.text(f"The Nominatim Search URL will be used to query OSM Country Boundary is: \n{response_url}")

        if query_url is None:
            set_state(1)
        else:
            st.button("Get/Display The OSM Country Boundary", on_click=set_state, args=[2])

    if st.session_state.stage >= 2:
        st.write(f'Getting and displaying the OSM country boundary for "{entered_country_code}" ...')

        # test the query_result function
        country_gdf = convert_nominatim_search_url_to_gdf(response_url)
        country_centroid = get_gdf_centroid_coordinates(country_gdf)
        # print(country_centroid)
        display_osm_boundary(country_gdf, country_centroid)

        st.button("Start Over", on_click=set_state, args=[0])


def main():
    # Title
    st.title(APP_TITLE)
    st.header("Display Country Boundary from OSM (via Nominatim API) Based on Country Code")

    # Start the app
    osm_boundary_stmap()


if __name__ == "__main__":
    main()
