from astroquery.gaia import Gaia as gaia
from astropy.coordinates import SkyCoord
from astroquery.simbad import Simbad as simbad
import astropy.units as u
import urllib.parse

import requests

def gaia_api(
        object_name,
        ra,
        dec,
        gaia_database, 
        radius = 0.01, # arc sec
        output_format = 'json'
):
    
    """
    GAIA API uses the GAIA Archive database to fetch the data for the given object. This is done using the 
    Astroquery.qaia module available with python. 

    Args:
        object_name (str): The name of the astronomical object (e.g., 'M 31', 'hd1').
                           Defaults to None.
        ra (float): Right Ascension in decimal degrees. Required for cone search.
                    Defaults to None.
        dec (float): Declination in decimal

    Returns:
        url (str): The fully constructed URL for accessing the data with GAIA Archive.
    """

    base_url = f"https://gea.esac.esa.int/tap-server/tap/sync?REQUEST=doQuery&LANG=ADQL&FORMAT={output_format}&QUERY="

    # if object_name:
    #     query = "Select top 2 source_id, ra, dec from {gaia_database}.gaiasource where"
    adql_query = None

    if object_name:
        # perfom a cone search with the object name
        # conver the object into prespective ra dec positions
        simbad_data = simbad.query_object(object_name)

        coord = SkyCoord(ra = simbad_data["ra"][0], dec = simbad_data['dec'][0], unit=(u.hourangle, u.deg))
        try: 
            # query = gaia.cone_search_async(coord, radius = radius * u.deg, table_name=gaia_database)
            adql_query = f"""SELECT TOP 5 source_id, ra, dec, parallax, pmra, pmdec FROM gaia{gaia_database}.gaia_source  WHERE 1 = CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', {coord.ra.deg}, {coord.dec.deg}, {radius}))"""
    
        except Exception as e:
            raise ValueError(f"Error in gaia searching {object_name}: {e} ")

    elif ra and dec:
        #use the ra and dec to do a cone search and find sources to a circluar region defined by the ra, dec and radius
        coord = SkyCoord(ra ,dec, unit=(u.degree, u.degree), frame='icrs')
        adql_query = f""" Select top 5 *, DISTANCE({coord.ra.deg}, {coord.dec.deg}, ra, dec) AS ang_sep from gaia{gaia_database}.gaia_source where distance({coord.ra.deg}, {coord.dec.deg}, ra, dec) < {radius} ORDER by ang_sep ASC """
        # query = gaia.cone_search(coord, radius = u.Quantity(radius, u.deg))
    
    encoded_query = urllib.parse.quote(adql_query)
    urli = f"{base_url}{encoded_query}"

    return urli