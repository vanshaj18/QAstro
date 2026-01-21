from typing import Optional, Union
import requests
import json
from core.gaia import gaia_api
from core.irsa import irsa_api, irsa_submit_async_job, irsa_wait_for_job, build_irsa_query
from core.ned import ned_api
from core.sdss import sdss_api
from core.simbad import simbad_api
from core.viser import viser_api
from core.ads import ads_api, get_ads_headers
from core.full_search import full_search_api
from core.middleware.middleware import middleware
from core.logger.logger import setup_logger

logger = setup_logger(__name__)

def data_fetcher(object_name, 
                    ra, 
                    dec, 
                    bibcode, 
                    database: str,
                    extra_options,
                    wavelength="Select Wavelength",
                    use_async_irsa: bool = False,
                ):
    """
    Based on the selected inputs, the function fetches the data as per the database selected.

    Args:
        - Name of the astronomical object
        - Coordinates in RA, DEC pairs
        - Bibcode for searching using the article published
        - Database to search in, SIMBAD, VISER, SDSS, ADS, GAIA Archive and more 


    Returns:
        str: The fetched data from the selected database.

    Raises:
        ValueError: If insufficient or incompatible parameters are provided, or if RA/DEC
                    are not in proper format.
    """
    logger.debug(f"Starting data fecthing: Parameters: object_name={object_name}, ra={ra}, dec={dec}, bibcode={bibcode}, database={database}, extra_options={extra_options}, wavelength={wavelength}, use_async_irsa={use_async_irsa}")
    data = None

    if database == "NONE":
        raise ValueError("No database selected. Select database")

    if database == "SIMBAD":
        url = simbad_api(object_name, ra, dec, bibcode)
        logger.debug(f"SIMBAD API URL: {url}")
    elif database == "VizieR": #remaining 
        url = viser_api(object_name, ra, dec, wavelength)
        logger.debug(f"VizieR API URL: {url}")
    elif database == "NED": #fix the HTML response
        url = ned_api( object_name, ra, dec, bibcode) # return a HTML response
        logger.debug(f"NED API URL: {url}")
    elif database == "SDSS":
        url = sdss_api(object_name, ra, dec, extra_options)
        logger.debug(f"SDSS API URL: {url}")
    elif database == "IRSA":
        if use_async_irsa:
            # Handle async IRSA query workflow
            try:
                # Build the ADQL query (using default radius of 0.1 degrees)
                adql_query, coord = build_irsa_query(object_name, ra, dec, extra_options, radius=0.1)
                logger.debug(f"IRSA ADQL query: {adql_query}")
                # Submit async job
                job_id = irsa_submit_async_job(adql_query, output_format='CSV')
                logger.debug(f"IRSA job ID: {job_id}")
                # Wait for job completion and get results
                data = irsa_wait_for_job(job_id, max_wait_time=300, poll_interval=5)
                logger.debug(f"IRSA data: {data}")
                return data
            except Exception as e:
                logger.warning(f"Error in async IRSA query: {str(e)}")
                raise ValueError(f"Error in async IRSA query: {str(e)}")
        else:
            # Synchronous query
            url = irsa_api(object_name, ra, dec, extra_options, use_async=False)
            logger.debug(f"IRSA API URL: {url}")
    elif database == "NASA ADS":
        url = ads_api(object_name, bibcode, extra_options.get('author') if extra_options else None, 
                     extra_options.get('year_range') if extra_options else None)
        logger.debug(f"NASA ADS API URL: {url}")
        # NASA ADS requires special headers with API key
        try:
            headers = get_ads_headers()
            data = requests.get(url, headers=headers)
            logger.debug(f"NASA ADS data: {data}")
            return data
        except ValueError as e:
            # Handle API key errors gracefully
            logger.warning(f"NASA ADS API error: {str(e)}")
            raise ValueError(f"NASA ADS API error: {str(e)}")
        except Exception as e:
            logger.warning(f"Error querying NASA ADS: {str(e)}")
            raise ValueError(f"Error querying NASA ADS: {str(e)}")
    
    elif database == "GAIA ARCHIVE":
        url = gaia_api(object_name, ra, dec, extra_options)
        logger.debug(f"GAIA ARCHIVE API URL: {url}")
    else: # this will be the case of ALL the databases
        full_data = full_search_api(
            object_name=object_name,
            ra=float(ra) if ra else None,
            dec=float(dec) if dec else None,
            bibcode=bibcode,
            extra_options=extra_options,
            wavelength=wavelength,
            use_async_irsa=use_async_irsa,
            output_format='json',
            use_async=True
        )
        # full_data is a dict of database names -> response objects
        return middleware(full_data)

    data = requests.get(url)
    # Single response object - pass through middleware
    logger.debug(f"Passing the data through middleware: {data}")
    return middleware(data)
