from typing import Optional
import urllib.parse

# Base URLs for different SIMBAD query types
# BASE_URL_ID = "https://simbad.cds.unistra.fr/simbad/sim-id"
# BASE_URL_CONE = "https://simbad.cds.unistra.fr/cone/"
# BASE_URL_REF = "https://simbad.cds.unistra.fr/simbad/sim-ref"
# BASE_URL_COO = "https://simbad.cds.unistra.fr/simbad/sim-coo" # Alternative for coords if needed
# BASE_URL_SAM = "https://simbad.cds.unistra.fr/simbad/sim-sam" # For criteria search (not directly built by this func)
BASE_TAP_URL = "https://simbad.cds.unistra.fr/simbad/sim-tap/sync?request=doQuery&lang=adql"

def simbad_api(object_name = None,
            ra = None, 
            dec = None, 
            bibcode = None, 
            radius_deg = 0.1, 
            output_format = 'json',
                # radius_deg=0.1, # Search radius in degrees for cone search (SR parameter)
                # # Format for ID/Ref queries ('output.format')
                # # output_format_cone='json', # Format for Cone queries ('RESPONSEFORMAT')
                # #    max_records_cone=10, # MAXREC for cone search
                # #    verbosity_cone=1 # VERB for cone search (1=basic)
            ):
    """
    Constructs a SIMBAD query URL based on the provided inputs.

    We use the TAP service to query the SIMBAD database. It's a single url with a string query that returns data
    in the desired format.

    Args:
        object_name (str, optional): The name/identifier of the astronomical object
                                     (e.g., 'M 31', 'hd1'). Defaults to None.
        ra (float, optional): Right Ascension in decimal degrees. Required for cone search.
                              Defaults to None.
        dec (float, optional): Declination in decimal degrees. Required for cone search.
                               Defaults to None.
        bibcode (str, optional): The 19-digit ADS bibcode (e.g., '2006ApJ...636L..85S').
                                 Defaults to None.
        radius_deg (float, optional): The search radius in decimal degrees for cone search (SR).
                                      Defaults to 0.1.
        output_format_id_ref (str, optional): Desired output format for Identifier and Reference
                                              queries (e.g., 'ASCII', 'TSV', 'HTML', 'VOTable').
                                              Uses the 'output.format' parameter. Defaults to 'ASCII'.
        output_format_cone (str, optional): Desired output format for Cone Search queries
                                            (e.g., 'json', 'votable', 'tsv', 'csv', 'ascii').
                                            Uses the 'RESPONSEFORMAT' parameter. Defaults to 'json'.

    Returns:
        str: The fully constructed URL for the SIMBAD query.

    Raises:
        ValueError: If insufficient or incompatible parameters are provided, or if RA/DEC
                    are not numeric.
    """

    # params = {}
    base_url = BASE_TAP_URL
    query_type = None
    base_query_string =  f"""SELECT basic.OID, RA, DEC, main_id AS "Main identifier",coo_bibcode AS "Coord Reference", plx_value as "Parallax", rvz_radvel as "Radial velocity", galdim_majaxis, galdim_minaxis,galdim_angle AS "Galaxy ellipse angle" """

    # --- Determine Query Type based on Input Priority ---
    if object_name:
        query = base_query_string + f""" FROM basic JOIN ident ON oidref = oid WHERE id='{object_name}';"""
        query_type = 'identifier'

    elif ra is not None and dec is not None:
        query_type = 'cone_search'
        try:
            # Validate RA/DEC are numbers and convert to string for URL
            ra_str = str(float(ra))
            dec_str = str(float(dec))
        except (ValueError, TypeError):
             raise ValueError("RA and DEC must be numeric values (decimal degrees).")
        
        query = base_query_string + f""" FROM basic JOIN flux ON oidref = oid AND CONTAINS(POINT('ICRS', RA, DEC), CIRCLE('ICRS', {ra}, {dec}, {radius_deg})) = 1 ORDER BY "Main identifier";""" 

    elif bibcode:
        query = f""" SELECT basic.OID, main_id AS "Identifier", FROM has_ref JOIN basic ON oidref = oid JOIN ref ON oidbibref = oidbib, WHERE bibcode = {bibcode}, ORDER BY "Identifier";"""
        query_type = 'reference'

    else:
        # No valid combination of inputs provided
        raise ValueError("Please provide one of the following input combinations: "
                         "1. object_name, "
                         "2. both ra and dec, "
                         "3. bibcode.")

    # --- Construct the Full URL ---
    # urlencode handles proper encoding of parameter values (like spaces in object_name)
    # quote_via=urllib.parse.quote_plus ensures spaces become '+' if needed by the server,
    # which is common in older URL schemes, though %20 is standard now.
    query_string = urllib.parse.quote(query)
    final_url = f"{base_url}&format={output_format}&query={query_string}"
    return final_url
