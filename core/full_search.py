"""
This module is used to perform a full search across all the databases for the given object name, RA, DEC and Bibcode. 
"""

import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Dict, Any
import json


class ErrorResponse:
    """Mock response object for error cases."""
    def __init__(self, error_msg: str):
        self.text = ""
        self.status_code = 500
        self.error = error_msg


# Import all database API functions
from core.gaia import gaia_api
from core.irsa import irsa_api, irsa_submit_async_job, irsa_wait_for_job, build_irsa_query
from core.ned import ned_api
from core.sdss import sdss_api
from core.simbad import simbad_api
from core.viser import viser_api
from core.ads import ads_api, get_ads_headers


def _fetch_simbad(object_name: Optional[str], ra: Optional[float], dec: Optional[float], 
                  bibcode: Optional[str], output_format: str = 'json') -> requests.Response:
    """Fetch data from SIMBAD database."""
    url = simbad_api(object_name, ra, dec, bibcode, output_format=output_format)
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response


def _fetch_viser(object_name: Optional[str], ra: Optional[float], dec: Optional[float],
                 wavelength: Optional[str] = None, output_format: str = 'json') -> requests.Response:
    """Fetch data from VizieR database."""
    url = viser_api(object_name, ra, dec, wavelength, output_format=output_format)
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response


def _fetch_ned(object_name: Optional[str], ra: Optional[float], dec: Optional[float],
               bibcode: Optional[str], output_format: str = 'json') -> requests.Response:
    """Fetch data from NED database."""
    url = ned_api(object_name, ra, dec, bibcode, output_format=output_format)
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response


def _fetch_sdss(object_name: Optional[str], ra: Optional[float], dec: Optional[float],
                extra_options: Optional[str], output_format: str = 'json') -> requests.Response:
    """Fetch data from SDSS database."""
    url = sdss_api(object_name, ra, dec, extra_options, output_format=output_format)
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response


def _fetch_irsa(object_name: Optional[str], ra: Optional[float], dec: Optional[float],
                extra_options: Optional[str], use_async: bool = False, output_format: str = 'CSV') -> requests.Response:
    """Fetch data from IRSA database."""
    if use_async:
        # Use async IRSA workflow
        adql_query, coord = build_irsa_query(object_name, ra, dec, extra_options, radius=0.1)
        job_id = irsa_submit_async_job(adql_query, output_format=output_format)
        response = irsa_wait_for_job(job_id, max_wait_time=300, poll_interval=5)
        return response
    else:
        # Synchronous query
        url = irsa_api(object_name, ra, dec, extra_options, use_async=False, output_format=output_format)
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response


def _fetch_gaia(object_name: Optional[str], ra: Optional[float], dec: Optional[float],
               gaia_database: Optional[str] = "dr3", output_format: str = 'json') -> requests.Response:
    """Fetch data from GAIA Archive database."""
    url = gaia_api(object_name, ra, dec, gaia_database, output_format=output_format)
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response


def _fetch_ads(object_name: Optional[str], bibcode: Optional[str], author: Optional[str] = None,
               year_range: Optional[str] = None, output_format: str = 'json') -> requests.Response:
    """Fetch data from NASA ADS database."""
    url = ads_api(object_name, bibcode, author, year_range, output_format=output_format)
    headers = get_ads_headers()
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response


def full_search_api(
    object_name: Optional[str] = None,
    ra: Optional[float] = None,
    dec: Optional[float] = None,
    bibcode: Optional[str] = None,
    database: Optional[str] = None,
    extra_options: Optional[str] = None,
    wavelength: Optional[str] = None,
    use_async_irsa: bool = False,
    radius: float = 0.1,
    output_format: str = 'json',
    use_async: bool = True,
    max_wait_time: int = 300,
) -> Dict[str, Any]:
    """
    Performs a full search across all available databases concurrently for the given parameters.
    
    Args:
        object_name (str, optional): The name of the astronomical object (e.g., 'M 31', 'hd1').
        ra (float, optional): Right Ascension in decimal degrees. Can be string or float.
        dec (float, optional): Declination in decimal degrees. Can be string or float.
        bibcode (str, optional): The 19-digit ADS bibcode (e.g., '2006ApJ...636L..85S').
        database (str, optional): Not used in full search - searches all databases.
        extra_options (str, optional): Additional options for IRSA queries (e.g., 'ALL_WISE', '2MASS').
        wavelength (str, optional): The wavelength to search in for VizieR (e.g., 'Optical', 'IR', 'UV').
        use_async_irsa (bool): Whether to use asynchronous IRSA queries. Defaults to False.
        radius (float): The search radius in degrees. Defaults to 0.1.
        output_format (str): Output format for queries. Defaults to 'json'.
        use_async (bool): Whether to run database queries concurrently. Defaults to True.
        max_wait_time (int): Maximum wait time for async IRSA jobs in seconds. Defaults to 300.
    
    Returns: 
        Dict[str, requests.Response]: Dictionary containing response objects from all databases with database name as key.
                                      Each database name maps to a requests.Response object.
    """
    # Convert ra/dec to float if they are strings
    try:
        ra = float(ra) if ra and isinstance(ra, (str, int, float)) else None
    except (ValueError, TypeError):
        ra = None
    
    try:
        dec = float(dec) if dec and isinstance(dec, (str, int, float)) else None
    except (ValueError, TypeError):
        dec = None
    
    full_search_data = {}
    
    # Prepare tasks for all databases
    tasks = []
    
    # SIMBAD - requires object_name, ra/dec, or bibcode
    if object_name or (ra is not None and dec is not None) or bibcode:
        tasks.append(("SIMBAD", _fetch_simbad, (object_name, ra, dec, bibcode, output_format)))
    
    # VizieR - requires object_name or ra/dec
    if object_name or (ra is not None and dec is not None):
        tasks.append(("VizieR", _fetch_viser, (object_name, ra, dec, wavelength, output_format)))
    
    # NED - requires object_name or ra/dec
    if object_name or (ra is not None and dec is not None):
        tasks.append(("NED", _fetch_ned, (object_name, ra, dec, bibcode, output_format)))
    
    # SDSS - requires ra/dec
    if ra is not None and dec is not None:
        tasks.append(("SDSS", _fetch_sdss, (object_name, ra, dec, extra_options, output_format)))
    
    # IRSA - requires object_name or ra/dec, and extra_options
    if (object_name or (ra is not None and dec is not None)) and extra_options and extra_options != "NONE":
        tasks.append(("IRSA", _fetch_irsa, (object_name, ra, dec, extra_options, use_async_irsa, output_format)))
    
    # GAIA ARCHIVE - requires object_name or ra/dec, and gaia_database
    gaia_db = extra_options if extra_options and extra_options in ["dr1", "dr2", "dr3"] else "dr3"
    if object_name or (ra is not None and dec is not None):
        tasks.append(("GAIA ARCHIVE", _fetch_gaia, (object_name, ra, dec, gaia_db, output_format)))
    
    # NASA ADS - requires object_name, bibcode, or author
    if object_name or bibcode:
        # Extract author and year_range from extra_options if it's a dict (for ADS)
        author = None
        year_range = None
        if isinstance(extra_options, dict):
            author = extra_options.get('author')
            year_range = extra_options.get('year_range')
        tasks.append(("NASA ADS", _fetch_ads, (object_name, bibcode, author, year_range, output_format)))
    
    if not tasks:
        return {"error": "No valid search parameters provided. Need at least object_name, ra/dec, or bibcode."}
    
    # Execute tasks concurrently or sequentially
    if use_async:
        # Use ThreadPoolExecutor for concurrent execution
        with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
            # Submit all tasks
            future_to_db = {
                executor.submit(func, *args): db_name 
                for db_name, func, args in tasks
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_db):
                db_name = future_to_db[future]
                try:
                    response = future.result()
                    full_search_data[db_name] = response
                except Exception as e:
                    # Create an error response object for consistency
                    full_search_data[db_name] = ErrorResponse(str(e))
    else:
        # Sequential execution
        for db_name, func, args in tasks:
            try:
                response = func(*args)
                full_search_data[db_name] = response
            except Exception as e:
                # Create an error response object for consistency
                full_search_data[db_name] = ErrorResponse(str(e))
    
    return full_search_data