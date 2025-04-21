from typing import Optional
import requests
from core.gaia import gaia_api
from core.iras import iras_api
from core.ned import ned_api
from core.sdss import sdss_api
from core.simbad import simbad_api
from core.viser import viser_api

#base urls
iras_base_url = "https://irsa.ipac.caltech.edu/SCS?"

def data_fetcher(object_name, 
                    ra, 
                    dec, 
                    bibcode, 
                    database: str,
                    extra_options,
                    wavelength="Select Wavelength",
                ):
    """
    Based on the selected inputs, the function fetches the data as per the database selected.

    Args:
        - Name of the astronomical object
        - Coordinates in RA, DEC pairs
        - Bibcode for searching using the article published
        - Database to search in, SIMBAD, VISER, SDSS, ADS, GAIA Archive and more 


    Returns:
        str: The fetched data from the selected database.

    Raises:
        ValueError: If insufficient or incompatible parameters are provided, or if RA/DEC
                    are not in proper format.
    """
    data = None

    if database == "NONE":
        raise ValueError("No database selected. Select database")

    if database == "SIMBAD":
        url = simbad_api(object_name, ra, dec, bibcode)

    elif database == "VizieR": #remaining 
        url = viser_api(object_name, ra, dec, wavelength)

    elif database == "NED": #fix the HTML response
        url = ned_api( object_name, ra, dec, bibcode) # return a HTML response

    elif database == "SDSS":
        url = sdss_api(object_name, ra, dec, extra_options)

    elif database == "IRAS":
        url = iras_api(object_name, ra, dec, extra_options)

    # elif database == "ADS":
    #     nasa_ads_data = nasa_ads_api()
    #     return nasa_ads_data
    
    elif database == "GAIA ARCHIVE":
        url = gaia_api(object_name, ra, dec, extra_options)
        
    # else: # this will be the case of ALL the databases
    #     full_data = full_search_api()
    #     return full_data

    data = requests.get(url)
    return data
