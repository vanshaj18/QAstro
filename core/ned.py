import urllib.parse

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
    if output_format == 'json':
        # Enhanced JSON-like output using pre_text format
        base_url = "https://ned.ipac.caltech.edu/cgi-bin/nph-objsearch"
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
        
        if object_name:
            params['objname'] = object_name
        elif ra is not None and dec is not None:
            # Coordinate-based search with radius
            params['in_csys'] = 'Equatorial'
            params['in_equinox'] = 'J2000.0'
            params['lon'] = str(ra)
            params['lat'] = str(dec)
            params['radius'] = str(radius_arcmin)
        elif bibcode:
            # Note: NED doesn't directly support bibcode searches in this interface
            # This would need to be handled differently or through a different endpoint
            raise ValueError("Bibcode search not supported in current NED implementation")
        else:
            raise ValueError("Either object_name or ra/dec coordinates must be provided")
        
        query_string = urllib.parse.urlencode(params)
        return f"{base_url}?{query_string}"
    
    else:
        # Fallback to existing HTML implementation for backward compatibility
        return _ned_api_html(object_name, ra, dec, bibcode)


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
    base_url = "https://ned.ipac.caltech.edu/cgi-bin/nph-objsearch?"

    if object_name:
        query = f"{object_name}"
    else:
        raise ValueError("Object name must be provided for HTML format")

    encode_query = urllib.parse.quote(query)
    url = f"{base_url}objname={encode_query}"

    return url