from astroquery.gaia import Gaia as gaia
from astropy.coordinates import SkyCoord
from astroquery.simbad import Simbad as simbad
import astropy.units as u
import urllib.parse
import requests
from core.logger.logger import setup_logger

logger = setup_logger(__name__)

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

    logger.info(f"Starting gaia_api function")
    logger.debug(f"Parameters: object_name={object_name}, ra={ra}, dec={dec}, gaia_database={gaia_database}, radius={radius}, output_format={output_format}")

    try:
        base_url = f"https://gea.esac.esa.int/tap-server/tap/sync?REQUEST=doQuery&LANG=ADQL&FORMAT={output_format}&QUERY="
        logger.debug(f"Base URL: {base_url}")
        adql_query = None

        if object_name:
            # perfom a cone search with the object name
            # conver the object into prespective ra dec positions
            logger.debug(f"Querying SIMBAD for object: {object_name}")
            simbad_data = simbad.query_object(object_name)

            coord = SkyCoord(ra = simbad_data["ra"][0], dec = simbad_data['dec'][0], unit=(u.hourangle, u.deg))
            logger.debug(f"Got coordinates from SIMBAD: ra={coord.ra.deg}, dec={coord.dec.deg}")
            try:
                adql_query = f"""SELECT * FROM gaia{gaia_database}.gaia_source WHERE source_id = '{object_name}'"""
                logger.debug(f"Built object query: {adql_query}")

            except Exception as e:
                logger.warning(f"Error in gaia searching {object_name}: {e}")
                raise ValueError(f"Error in gaia searching {object_name}: {e} ")

        elif ra and dec:
            #use the ra and dec to do a cone search and find sources to a circluar region defined by the ra, dec and radius
            logger.debug(f"Using provided coordinates for cone search: ra={ra}, dec={dec}, radius={radius}")
            coord = SkyCoord(ra ,dec, unit=(u.degree, u.degree), frame='icrs')
            adql_query = f""" Select top 5 *, DISTANCE({coord.ra.deg}, {coord.dec.deg}, ra, dec) AS ang_sep from gaia{gaia_database}.gaia_source where distance({coord.ra.deg}, {coord.dec.deg}, ra, dec) < {radius} ORDER by ang_sep ASC """
            logger.debug(f"Built cone search query: {adql_query}")
            # query = gaia.cone_search(coord, radius = u.Quantity(radius, u.deg))

        encoded_query = urllib.parse.quote(adql_query)
        urli = f"{base_url}{encoded_query}"
        logger.debug(f"Final URL: {urli}")

        return urli

    except Exception as e:
        logger.warning(f"Error in gaia_api function: {str(e)}")
        raise