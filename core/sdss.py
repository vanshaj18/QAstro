import urllib
from core.logger.logger import setup_logger

logger = setup_logger(__name__)

def sdss_api(
        obj_name,
        ra,
        dec,
        extra_options,
        radius = 1, #arc minutes
        output_format='json'
):
    """
    Constructs a SDSS query URL based on the provided inputs. The function uses the SQL Search method provided by the
    SDSS Database.

    Args:
        obj_name (str): The name of the astronomical object (e.g., 'M 31', 'hd1').
                        Defaults to None.
        ra (float): Right Ascension in decimal degrees. Required for cone search.
                    Defaults to None.
        dec (float): Declination in decimal degrees. Required for cone search.
                     Defaults to None.
        bibcode (str): The 19-digit ADS bibcode (e.g., '2006ApJ...636L..85S').
                       Defaults to None.
        output_format (str): Desired output format for the query (e.g., 'json', 'csv').
                             Defaults to 'json'.

    Returns:
        str: The fully constructed URL for the SDSS query.

    """
    logger.info(f"Starting sdss_api function")
    logger.debug(f"Parameters: obj_name={obj_name}, ra={ra}, dec={dec}, radius={radius}, output_format={output_format}")

    try:
        base_url = f"http://skyserver.sdss.org/dr18/SkyServerWS/SearchTools/SqlSearch?format={output_format}&cmd="
        logger.debug(f"Base URL: {base_url}")

        # given the RA DEC for an object, we use the cone search method
        if ra and dec:
            query = f"select top 2 * from dbo.fGetNearbyObjEq({ra}, {dec}, {radius})"
            logger.debug(f"Generated query: {query}")
        else:
            logger.warning("No RA/DEC coordinates provided for cone search")

        query_string = urllib.parse.quote(query)
        final_url = f"{base_url}{query_string}"
        logger.debug(f"Final URL: {final_url}")

        return final_url

    except Exception as e:
        logger.warning(f"Error in sdss_api function: {str(e)}")
        raise