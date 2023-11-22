import json
import requests
import streamlit as st

from services.nominatim_services import (
    convert_nominatim_search_url_to_gdf,
    display_osm_boundary,
)

from models.nominatim_models import nominatim_country_codes


def set_state(i):
    st.session_state.stage = i


def osm_boundary_stmap():
    if "stage" not in st.session_state:
        st.session_state.stage = 0

    if st.session_state.stage >= 0:
        
        st.write(
            "From this list of OSM country codes: https://wiki.openstreetmap.org/wiki/Nominatim/Country_Codes"
        )

        entered_country_code = st.selectbox(
            "Please select the country code that you want to display",
            nominatim_country_codes.__args__,
            index=None,
            placeholder="Select the country code ....",
            on_change=set_state,
            args=[1],
        )

    if st.session_state.stage >= 1:

        if entered_country_code is not None:

            st.write(f'You entered: "{entered_country_code}"')

            inputs = {"country_code": entered_country_code}
            response_url = requests.post(
                "http://localhost:8000/create/nominatim_search_url",
                data=json.dumps(inputs),
            ).json()
            print(f"Nominatim Search URL: {response_url}")

            sttext_url = st.text(f"The Nominatim Search URL will be used to query OSM Country Boundary is: \n{response_url}")

            if sttext_url is None:
                set_state(1)
            else:
                st.button("Fetch OSM Boundary", on_click=set_state, args=[2])

    if st.session_state.stage >= 2:

        if sttext_url is not None:
            
            st.write(f'Displaying the OSM boundary for "{entered_country_code}" ...')
            country_gdf, country_centroid = convert_nominatim_search_url_to_gdf(response_url)
            display_osm_boundary(country_gdf, country_centroid)

            st.button("Start Over", on_click=set_state, args=[0])


def main():
    APP_TITLE = "FastAPI & Streamlit - Demo Map"

    # Title
    st.title(APP_TITLE)
    st.header("Display Country Boundary from OSM (via Nominatim API) Based on Country Code")

    # Start the app
    osm_boundary_stmap()


if __name__ == "__main__":
    main()
