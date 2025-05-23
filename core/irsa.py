from astroquery.simbad import Simbad as simbad
from astropy.coordinates import SkyCoord
import astropy.units as u
import urllib.parse

def irsa_api( object_name, ra, dec, extra_options, radius = 0.1, output_format='CSV'):
    """
    Constructs a URL for querying the IRSA database based on the provided parameters.
    
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
        str: The fully constructed URL for the IRSA query.
    """
    base_url = f"https://irsa.ipac.caltech.edu/TAP/sync?QUERY="

    #creating service object
    # service = vo.dal.TAPService("https://irsa.ipac.caltech.edu/TAP")

    #given the name of the object, we use SIMBAD to get the coordinates
    simbad_data = simbad.query_object(object_name)
    coord = SkyCoord(ra = simbad_data["ra"][0], dec = simbad_data['dec'][0], unit=(u.hourangle, u.deg))

    #based on the selected options, we need to select the appropriate table in IRSA
    table_name = None
    table_query = "Select TOP 5"

    if extra_options == "ALL_WISE":
        table_name = "allwise_p3as_psd"
        table_query = table_query + " ra,dec, w1mpro, w1sigmpro, w2mpro, w2sigmpro, w3mpro, w3sigmpro, w4mpro, w4sigmpro, cc_flags"

    if extra_options == "2MASS":
        table_name = "fp_psc"
        table_query = table_query + " ra,dec,j_m,j_msigcom,h_m,h_msigcom,k_m,k_msigcom,ph_qual,cc_flg"

    elif extra_options == "GLIMPSE_I":
        table_name = "glimpse_s07"
        table_query+= " *"

    elif extra_options == "COSMOS":
        table_name = "cosmos_phot" 
        table_query+= " *"
        
    elif extra_options == "IRAS":
        table_name = "iraspsc"
        table_query += " *"
    
    adql_query = table_query + f" from {table_name} WHERE CONTAINS(POINT('ICRS',ra, dec), CIRCLE('ICRS',{coord.ra.deg},{coord.dec.deg},{radius}))=1"
    
    # service_result = service.run_async(adql_query)
    # tab = service_result.to_table()
    encoded_query = urllib.parse.quote(adql_query)
    final_query = f"{base_url}{encoded_query}&FORMAT={output_format}"

    return final_query