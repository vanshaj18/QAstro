import urllib

def ned_api(object_name, ra, dec, bibcode, output_format='json'):
    """
    NED Database maintained by NASA. Its used for Cataloging ExtraGalactic Objects.
    
    Args:
        - object_name: Name of the astronomical object
        - ra: Right Ascension in degrees
        - dec: Declination in degrees
        - bibcode: Bibcode for searching using the article published
        - radius_deg: Search radius in degrees
        - output_format: Output format (json, csv, etc.)
    
    Returns:
        - str: The constructed URL for the NED API call.
    
    """
    base_url = "https://ned.ipac.caltech.edu/cgi-bin/nph-objsearch?"

    if object_name:
        query = f"{object_name}"
    # elif ra is not None and dec is not None:
    #     query = f"RA={ra}&DEC={dec}"
    # elif bibcode:
    #     query = f"bibcode={bibcode}"
    else:
        raise ValueError("At least one of object_name, ra/dec, or bibcode must be provided.")

    encode_query = urllib.parse.quote(query)
    url = f"{base_url}objname={encode_query}"

    return url