from astroquery.simbad import Simbad as simbad
from astropy.coordinates import SkyCoord
import astropy.units as u
import urllib.parse
import requests
import time
from typing import Optional, Tuple, Dict
from core.logger.logger import setup_logger

logger = setup_logger(__name__)

def build_irsa_query(object_name: Optional[str], ra: Optional[float], dec: Optional[float],
                      extra_options: str, radius: float = 0.1) -> Tuple[str, SkyCoord]:
    """
    Builds the ADQL query for IRSA and gets coordinates.

    Returns:
        tuple: (adql_query_string, SkyCoord object)
    """
    logger.info(f"Starting build_irsa_query function")
    logger.debug(f"Parameters: object_name={object_name}, ra={ra}, dec={dec}, extra_options={extra_options}, radius={radius}")

    try:
        coord = None
    
        # Get coordinates from object name or use provided coordinates
        if object_name:
            logger.debug(f"Querying SIMBAD for object: {object_name}")
            simbad_data = simbad.query_object(object_name)
            coord = SkyCoord(ra=simbad_data["ra"][0], dec=simbad_data['dec'][0], unit=(u.hourangle, u.deg))
            logger.debug(f"Got coordinates from SIMBAD: ra={coord.ra.deg}, dec={coord.dec.deg}")
        elif ra is not None and dec is not None:
            coord = SkyCoord(ra=ra, dec=dec, unit=(u.degree, u.degree), frame='icrs')
            logger.debug(f"Using provided coordinates: ra={ra}, dec={dec}")
        else:
            logger.warning("Either object_name or both ra and dec must be provided")
            raise ValueError("Either object_name or both ra and dec must be provided")

        # Build query based on selected options
        table_name = None
        table_query = "Select TOP 5"
        logger.debug(f"Building query for extra_options: {extra_options}")

        if extra_options == "ALL_WISE":
            table_name = "allwise_p3as_psd"
            table_query = table_query + " ra,dec, w1mpro, w1sigmpro, w2mpro, w2sigmpro, w3mpro, w3sigmpro, w4mpro, w4sigmpro, cc_flags"
        elif extra_options == "2MASS":
            table_name = "fp_psc"
            table_query = table_query + " ra,dec,j_m,j_msigcom,h_m,h_msigcom,k_m,k_msigcom,ph_qual,cc_flg"
        elif extra_options == "GLIMPSE_I":
            table_name = "glimpse_s07"
            table_query += " *"
        elif extra_options == "COSMOS":
            table_name = "cosmos_phot"
            table_query += " *"
        elif extra_options == "IRAS":
            table_name = "iraspsc"
            table_query += " *"
        else:
            logger.warning(f"Invalid extra_options: {extra_options}")
            raise ValueError(f"Invalid extra_options: {extra_options}. Must be one of: ALL_WISE, 2MASS, GLIMPSE_I, COSMOS, IRAS")

        adql_query = table_query + f" from {table_name} WHERE CONTAINS(POINT('ICRS',ra, dec), CIRCLE('ICRS',{coord.ra.deg},{coord.dec.deg},{radius}))=1"
        logger.debug(f"Built ADQL query: {adql_query}")

        return adql_query, coord

    except Exception as e:
        logger.warning(f"Error in build_irsa_query function: {str(e)}")
        raise


def irsa_submit_async_job(adql_query: str, output_format: str = 'CSV', upload: Optional[str] = None) -> str:
    """
    Submits an async job to IRSA TAP service.

    Args:
        adql_query: The ADQL query string
        output_format: Output format (CSV, JSON, VOTABLE, etc.)
        upload: Optional UPLOAD parameter for table uploads

    Returns:
        str: Job ID extracted from the Location header or response

    Raises:
        ValueError: If job submission fails
    """
    logger.info(f"Starting irsa_submit_async_job function")
    logger.debug(f"Parameters: output_format={output_format}, upload={upload}")

    try:
        base_url = "https://irsa.ipac.caltech.edu/TAP/async"
        logger.debug(f"Base URL: {base_url}")
    
        params = {
            'QUERY': adql_query,
            'FORMAT': output_format
        }

        if upload:
            params['UPLOAD'] = upload
            logger.debug(f"Added upload parameter: {upload}")

        logger.debug(f"Submitting async job with params: {params}")
        response = requests.post(base_url, params=params, allow_redirects=False)

        if response.status_code in [303, 302]:
            # Extract job ID from Location header
            location = response.headers.get('Location', '')
            logger.debug(f"Redirect location: {location}")
            # Location format: https://irsa.ipac.caltech.edu/TAP/async/35
            job_id = location.rstrip('/').split('/')[-1]
            logger.debug(f"Extracted job ID: {job_id}")
            return job_id
        elif response.status_code == 200:
            # Sometimes the job ID is in the response body
            # Try to extract from response
            content = response.text
            logger.debug(f"Response content length: {len(content)}")
            # Look for job ID in various formats
            import re
            match = re.search(r'/async/(\d+)', content)
            if match:
                job_id = match.group(1)
                logger.debug(f"Extracted job ID from response: {job_id}")
                return job_id
            logger.warning(f"Could not extract job ID from response. Status: {response.status_code}")
            raise ValueError(f"Could not extract job ID from response. Status: {response.status_code}")
        else:
            logger.warning(f"Failed to submit async job. Status: {response.status_code}")
            raise ValueError(f"Failed to submit async job. Status: {response.status_code}, Response: {response.text}")

    except Exception as e:
        logger.warning(f"Error in irsa_submit_async_job function: {str(e)}")
        raise


def irsa_check_job_status(job_id: str) -> str:
    """
    Checks the status of an async IRSA job.

    Args:
        job_id: The job ID returned from irsa_submit_async_job

    Returns:
        str: Job phase (QUEUED, EXECUTING, COMPLETED, ERROR, ABORT)

    Raises:
        ValueError: If status check fails
    """
    logger.debug(f"Checking job status for job_id: {job_id}")

    try:
        status_url = f"https://irsa.ipac.caltech.edu/TAP/async/{job_id}/phase"
        logger.debug(f"Status URL: {status_url}")

        response = requests.get(status_url)

        if response.status_code == 200:
            status = response.text.strip()
            logger.debug(f"Job status: {status}")
            return status
        else:
            logger.warning(f"Failed to check job status. Status: {response.status_code}")
            raise ValueError(f"Failed to check job status. Status: {response.status_code}, Response: {response.text}")

    except Exception as e:
        logger.warning(f"Error in irsa_check_job_status function: {str(e)}")
        raise


def irsa_get_async_results(job_id: str) -> requests.Response:
    """
    Retrieves results from a completed async IRSA job.

    Args:
        job_id: The job ID returned from irsa_submit_async_job

    Returns:
        requests.Response: Response object containing the results

    Raises:
        ValueError: If job is not completed or retrieval fails
    """
    logger.debug(f"Retrieving async results for job_id: {job_id}")

    try:
        results_url = f"https://irsa.ipac.caltech.edu/TAP/async/{job_id}/results/result"
        logger.debug(f"Results URL: {results_url}")

        response = requests.get(results_url)

        if response.status_code == 200:
            logger.debug(f"Successfully retrieved results, content length: {len(response.text)}")
            return response
        else:
            logger.warning(f"Failed to retrieve results. Status: {response.status_code}")
            raise ValueError(f"Failed to retrieve results. Status: {response.status_code}, Response: {response.text}")

    except Exception as e:
        logger.warning(f"Error in irsa_get_async_results function: {str(e)}")
        raise


def irsa_wait_for_job(job_id: str, max_wait_time: int = 300, poll_interval: int = 5) -> requests.Response:
    """
    Waits for an async IRSA job to complete and returns results.

    Args:
        job_id: The job ID returned from irsa_submit_async_job
        max_wait_time: Maximum time to wait in seconds (default: 300 = 5 minutes)
        poll_interval: Time between status checks in seconds (default: 5)

    Returns:
        requests.Response: Response object containing the results

    Raises:
        ValueError: If job fails, times out, or is aborted
        TimeoutError: If max_wait_time is exceeded
    """
    logger.info(f"Starting irsa_wait_for_job for job_id: {job_id}")
    logger.debug(f"Parameters: max_wait_time={max_wait_time}, poll_interval={poll_interval}")

    try:
        start_time = time.time()

        while True:
            status = irsa_check_job_status(job_id)

            if status == "COMPLETED":
                logger.info(f"Job {job_id} completed successfully")
                return irsa_get_async_results(job_id)
            elif status == "ERROR":
                logger.warning(f"IRSA async job {job_id} failed with ERROR status")
                raise ValueError(f"IRSA async job {job_id} failed with ERROR status")
            elif status == "ABORT":
                logger.warning(f"IRSA async job {job_id} was aborted")
                raise ValueError(f"IRSA async job {job_id} was aborted")
            elif status in ["QUEUED", "EXECUTING"]:
                elapsed_time = time.time() - start_time
                logger.debug(f"Job {job_id} status: {status}, elapsed time: {elapsed_time:.1f}s")
                if elapsed_time > max_wait_time:
                    logger.warning(f"Job {job_id} exceeded max wait time of {max_wait_time} seconds")
                    raise TimeoutError(f"IRSA async job {job_id} exceeded max wait time of {max_wait_time} seconds. Current status: {status}")
                time.sleep(poll_interval)
            else:
                logger.warning(f"Unknown job status: {status}")
                raise ValueError(f"Unknown job status: {status}")

    except Exception as e:
        logger.warning(f"Error in irsa_wait_for_job function: {str(e)}")
        raise


def irsa_api(object_name: Optional[str] = None,
             ra: Optional[float] = None,
             dec: Optional[float] = None,
             extra_options: Optional[str] = None,
             radius: float = 0.1,
             output_format: str = 'CSV',
             use_async: bool = False,
             max_wait_time: int = 300,
             poll_interval: int = 5) -> str:
    """
    Constructs a URL for querying the IRSA database based on the provided parameters.
    Supports both synchronous and asynchronous queries for large searches.

    Args:
        object_name (str, optional): The name of the astronomical object (e.g., 'M 31', 'hd1').
                                     Defaults to None.
        ra (float, optional): Right Ascension in decimal degrees. Required if object_name not provided.
        dec (float, optional): Declination in decimal degrees. Required if object_name not provided.
        extra_options (str, optional): Additional options for the query. Must be one of:
                                      'ALL_WISE', '2MASS', 'GLIMPSE_I', 'COSMOS', 'IRAS'.
        radius (float): Search radius in degrees. Defaults to 0.1.
        output_format (str): Desired output format for the query (e.g., 'CSV', 'json', 'VOTABLE').
                             Defaults to 'CSV'.
        use_async (bool): If True, uses async endpoint for large queries. Defaults to False.
        max_wait_time (int): Maximum time to wait for async job completion in seconds. Defaults to 300.
        poll_interval (int): Time between status checks for async jobs in seconds. Defaults to 5.

    Returns:
        str: The fully constructed URL for the IRSA query (sync) or job submission URL (async).
              For async queries, this returns the async endpoint URL. Use irsa_submit_async_job,
              irsa_check_job_status, and irsa_get_async_results for full async workflow.

    Raises:
        ValueError: If insufficient or incompatible parameters are provided.
    """
    logger.info(f"Starting irsa_api function")
    logger.debug(f"Parameters: object_name={object_name}, ra={ra}, dec={dec}, extra_options={extra_options}, radius={radius}, output_format={output_format}, use_async={use_async}")

    try:
        if not extra_options or extra_options == "NONE":
            logger.warning("extra_options must be provided and cannot be 'NONE'")
            raise ValueError("extra_options must be provided and cannot be 'NONE'")

        # Build the ADQL query
        adql_query, coord = build_irsa_query(object_name, ra, dec, extra_options, radius)

        if use_async:
            # For async, return the async endpoint URL
            # Note: The actual async workflow requires using irsa_submit_async_job() and related functions
            base_url = "https://irsa.ipac.caltech.edu/TAP/async"
            logger.debug(f"Using async endpoint, base URL: {base_url}")
            encoded_query = urllib.parse.quote(adql_query)
            final_query = f"{base_url}?QUERY={encoded_query}&FORMAT={output_format}"
            logger.debug(f"Final async query URL: {final_query}")
            return final_query
        else:
            # Synchronous query
            base_url = "https://irsa.ipac.caltech.edu/TAP/sync?QUERY="
            logger.debug(f"Using sync endpoint, base URL: {base_url}")
            encoded_query = urllib.parse.quote(adql_query)
            final_query = f"{base_url}{encoded_query}&FORMAT={output_format}"
            logger.debug(f"Final sync query URL: {final_query}")
            return final_query

    except Exception as e:
        logger.warning(f"Error in irsa_api function: {str(e)}")
        raise