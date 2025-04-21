from astroquery.simbad import Simbad as simbad
from astropy.coordinates import SkyCoord
import astropy.units as u
import urllib.parse


def iras_api( object_name, ra, dec, extra_options, radius = 0.1, output_format='csv'):
    """
    Constructs a URL for querying the IRAS database based on the provided parameters.
    
    Args:
        object_name (str): The name of the astronomical object (e.g., 'M 31', 'hd1').
                           Defaults to None.
        ra (float): Right Ascension in decimal degrees. Required for cone search.
                    Defaults to None.
        dec (float): Declination in decimal degrees. Required for cone search.
                     Defaults to None.
        extra_options (str): Additional options for the query (e.g., 'ALL WISE', '2MASS').
                             Defaults to None.
        output_format (str): Desired output format for the query (e.g., 'json', 'csv').
                             Defaults to 'json'.
    
    Returns:
        str: The fully constructed URL for the IRAS query.
    """
    base_url = f"https://irsa.ipac.caltech.edu/TAP/sync?QUERY="

    #given the name of the object, we use SIMBAD to get the coordinates
    simbad_data = simbad.query_object(object_name)
    coord = SkyCoord(ra = simbad_data["ra"][0], dec = simbad_data['dec'][0], unit=(u.hourangle, u.deg))

    #based on the selected options, we need to select the appropriate table in IRAS
    table_name = None
    if extra_options == "ALLWISE":
        table_name = "allwise_p3as_psd"
    if extra_options == "2MASS":
        table_name = "fp_psc"
    elif extra_options == "GLIMPSE I":
        table_name = "glimpse_s07"
    elif extra_options == "COSMOS":
        table_name = "cosmos_phot" 
    elif extra_options == "IRAS Point Source":
        table_name = "iraspsc"
    # else: 
    #     raise ValueError(f"Invalid options for IRAS")
    
    adql_query = f"Select * from {table_name} WHERE CONTAINS(POINT('ICRS',ra, dec), CIRCLE('ICRS',{coord.ra.deg},{coord.dec.deg},{radius}))=1&FORMAT={output_format}"
    
    encoded_query = urllib.parse.quote(adql_query)
    
    final_query = f"{base_url}{encoded_query}"
    print(final_query)

    return final_query