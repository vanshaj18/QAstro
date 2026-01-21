import urllib.parse
from core.logger.logger import setup_logger

logger = setup_logger(__name__)

def ned_api(object_name=None, ra=None, dec=None, bibcode=None, radius_arcmin=2.0, output_format='json'):
    """
    Enhanced NED Database API for NASA/IPAC Extragalactic Database.
    Used for cataloging extragalactic objects with support for both JSON and HTML formats.

    Args:
        - object_name: Name of the astronomical object (optional)
        - ra: Right Ascension in degrees (optional)
        - dec: Declination in degrees (optional)
        - bibcode: Bibcode for searching using the article published (optional)
        - radius_arcmin: Search radius in arcminutes (default: 2.0)
        - output_format: Output format ('json' or 'html', default: 'json')

    Returns:
        - str: The constructed URL for the NED API call.

    Raises:
        - ValueError: If no search parameters are provided or invalid parameters
    """
    logger.info(f"Starting ned_api function")
    logger.debug(f"Parameters: object_name={object_name}, ra={ra}, dec={dec}, bibcode={bibcode}, radius_arcmin={radius_arcmin}, output_format={output_format}")

    try:
        if output_format == 'json':
            # Enhanced JSON-like output using pre_text format
            base_url = "https://ned.ipac.caltech.edu/cgi-bin/nph-objsearch"
            logger.debug(f"Base URL: {base_url}")
            params = {
                'extend': 'no',
                'hconst': '67.8',
                'omegam': '0.308',
                'omegav': '0.692',
                'corr_z': '1',
                'out_csys': 'Equatorial',
                'out_equinox': 'J2000.0',
                'obj_sort': 'RA or Longitude',
                'of': 'pre_text',  # For structured text output that can be parsed
                'zv_breaker': '30000.0',
                'list_limit': '5',
                'img_stamp': 'NO'
            }
            logger.debug(f"Initial params: {params}")

            if object_name:
                params['objname'] = object_name
                logger.debug(f"Added object_name parameter: {object_name}")
            elif ra is not None and dec is not None:
                # Coordinate-based search with radius
                params['in_csys'] = 'Equatorial'
                params['in_equinox'] = 'J2000.0'
                params['lon'] = str(ra)
                params['lat'] = str(dec)
                params['radius'] = str(radius_arcmin)
                logger.debug(f"Added coordinate parameters: ra={ra}, dec={dec}, radius={radius_arcmin}")
            elif bibcode:
                # Note: NED doesn't directly support bibcode searches in this interface
                # This would need to be handled differently or through a different endpoint
                logger.warning("Bibcode search not supported in current NED implementation")
                raise ValueError("Bibcode search not supported in current NED implementation")
            else:
                logger.warning("Either object_name or ra/dec coordinates must be provided")
                raise ValueError("Either object_name or ra/dec coordinates must be provided")

            query_string = urllib.parse.urlencode(params)
            final_url = f"{base_url}?{query_string}"
            logger.debug(f"Final URL: {final_url}")
            return final_url

        else:
            # Fallback to existing HTML implementation for backward compatibility
            logger.debug("Using HTML format fallback")
            return _ned_api_html(object_name, ra, dec, bibcode)

    except Exception as e:
        logger.warning(f"Error in ned_api function: {str(e)}")
        raise


def _ned_api_html(object_name=None, ra=None, dec=None, bibcode=None):
    """
    Legacy HTML implementation for backward compatibility.

    Args:
        - object_name: Name of the astronomical object
        - ra: Right Ascension in degrees (not implemented in legacy version)
        - dec: Declination in degrees (not implemented in legacy version)
        - bibcode: Bibcode for searching (not implemented in legacy version)

    Returns:
        - str: The constructed URL for the NED API call.
    """
    logger.debug(f"Starting _ned_api_html function with object_name: {object_name}")

    try:
        base_url = "https://ned.ipac.caltech.edu/cgi-bin/nph-objsearch?"
        logger.debug(f"Base URL: {base_url}")

        if object_name:
            query = f"{object_name}"
            logger.debug(f"Query: {query}")
        else:
            logger.warning("Object name must be provided for HTML format")
            raise ValueError("Object name must be provided for HTML format")

        encode_query = urllib.parse.quote(query)
        url = f"{base_url}objname={encode_query}"
        logger.debug(f"Final URL: {url}")

        return url

    except Exception as e:
        logger.warning(f"Error in _ned_api_html function: {str(e)}")
        raise