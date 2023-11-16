from fastapi import APIRouter

from models.nominatim_models import RequestNominatimSearchURL
from services.nominatim_services import create_nominatim_search_url


router = APIRouter(prefix="/create")

@router.post(
    "/nominatim_search_url",
    description="Create Nominatim's search URL based on queried country code string",
    status_code=201,
)
def get_nominatim_search_url(
    input: RequestNominatimSearchURL
):
    return create_nominatim_search_url(input.country_code)
