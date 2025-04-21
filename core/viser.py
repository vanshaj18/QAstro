
def viser_api(object_name=None, 
            ra = None, 
            dec = None, 
            wavelength = None,
            output_format = 'json'
        ):
    """
    Viser Database maintained by CDS.

    Args:
        - object_name: Name of the astronomical object
        - ra: Right Ascension in degrees
        - dec: Declination in degrees
        - bibcode: Bibcode for searching using the article published
        - radius_deg: Search radius in degrees
        - output_format: Output format (json, csv, etc.)

    Returns:
        - str: The constructed URL for the VizieR API call.
    
    """

    