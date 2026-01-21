import urllib.parse
import requests
from typing import Optional, List
from core.logger.logger import setup_logger

logger = setup_logger(__name__)

def get_wavelength_catalogs(wavelength: str) -> str:
    """
    Returns ADQL WHERE clause for filtering catalogs by wavelength.

    Args:
        wavelength: Wavelength category (Radio, IR, Optical, UV, EUV, X-Ray, Gamma)

    Returns:
        str: ADQL WHERE clause for catalog filtering
    """
    logger.debug(f"Starting get_wavelength_catalogs function with wavelength: {wavelength}")

    try:
        wavelength_filters = {
            "Radio": "AND (cat_name LIKE '%radio%' OR cat_name LIKE '%cm%' OR cat_name LIKE '%mm%')",
            "IR": "AND (cat_name LIKE '%ir%' OR cat_name LIKE '%infrared%' OR cat_name LIKE '%2mass%' OR cat_name LIKE '%wise%')",
            "Optical": "AND (cat_name LIKE '%optical%' OR cat_name LIKE '%visual%' OR cat_name LIKE '%gsc%' OR cat_name LIKE '%usno%')",
            "UV": "AND (cat_name LIKE '%uv%' OR cat_name LIKE '%ultraviolet%' OR cat_name LIKE '%galex%')",
            "EUV": "AND (cat_name LIKE '%euv%' OR cat_name LIKE '%extreme%')",
            "X-Ray": "AND (cat_name LIKE '%xray%' OR cat_name LIKE '%x-ray%' OR cat_name LIKE '%rosat%' OR cat_name LIKE '%chandra%')",
            "Gamma": "AND (cat_name LIKE '%gamma%' OR cat_name LIKE '%fermi%')"
        }
        result = wavelength_filters.get(wavelength, "")
        logger.debug(f"Wavelength filter result: {result}")
        return result
    except Exception as e:
        logger.warning(f"Error in get_wavelength_catalogs function: {str(e)}")
        raise

def build_vizier_object_query(object_name: str, catalog_filter: str = "") -> str:
    """
    Build ADQL query for object name search in VizieR.

    Args:
        object_name: Name of the astronomical object
        catalog_filter: Optional catalog filtering clause

    Returns:
        str: ADQL query string
    """
    logger.debug(f"Starting build_vizier_object_query function with object_name: {object_name}, catalog_filter: {catalog_filter}")

    try:
        # Use a basic query that searches for the object name across VizieR catalogs
        query = f"""SELECT TOP 100 cat_name, table_name, raj2000 as ra, dej2000 as dec, main_id, recno FROM "METAcatalog" as meta JOIN "METAtab" as tab ON meta.catid = tab.catid WHERE CONTAINS(POINT('ICRS', raj2000, dej2000), CIRCLE('ICRS', (SELECT raj2000 FROM "SIMBAD"."basic" WHERE main_id = '{object_name}'), (SELECT dej2000 FROM "SIMBAD"."basic" WHERE main_id = '{object_name}'), 0.1)) = 1 {catalog_filter} ORDER BY cat_name"""
        result = query.strip()
        logger.debug(f"Built object query: {result}")
        return result
    except Exception as e:
        logger.warning(f"Error in build_vizier_object_query function: {str(e)}")
        raise

def build_vizier_cone_query(ra: float, dec: float, radius_arcmin: float = 2.0, catalog_filter: str = "") -> str:
    """
    Build ADQL query for cone search in VizieR.

    Args:
        ra: Right Ascension in degrees
        dec: Declination in degrees
        radius_arcmin: Search radius in arcminutes
        catalog_filter: Optional catalog filtering clause

    Returns:
        str: ADQL query string
    """
    logger.debug(f"Starting build_vizier_cone_query function with ra: {ra}, dec: {dec}, radius_arcmin: {radius_arcmin}, catalog_filter: {catalog_filter}")

    try:
        radius_deg = radius_arcmin / 60.0  # Convert arcminutes to degrees
        logger.debug(f"Converted radius from {radius_arcmin} arcmin to {radius_deg} degrees")

        query = f""" SELECT TOP 100 cat_name, table_name, raj2000 as ra, dej2000 as dec, main_id, recno FROM "METAcatalog" as meta JOIN "METAtab" as tab ON meta.catid = tab.catid WHERE CONTAINS(POINT('ICRS', raj2000, dej2000), CIRCLE('ICRS', {ra}, {dec}, {radius_deg})) = 1 {catalog_filter} ORDER BY cat_name """
        result = query.strip()
        logger.debug(f"Built cone query: {result}")
        return result
    except Exception as e:
        logger.warning(f"Error in build_vizier_cone_query function: {str(e)}")
        raise

def viser_api(object_name: Optional[str] = None,
              ra: Optional[float] = None,
              dec: Optional[float] = None,
              wavelength: Optional[str] = None,
              radius_arcmin: float = 2.0,
              output_format: str = 'json') -> str:
    """
    VizieR Database API using CDS TAP service.

    VizieR is a comprehensive catalog service providing access to astronomical
    catalogs and surveys. This function constructs queries to search VizieR
    catalogs by object name or coordinates, with optional wavelength filtering.

    Args:
        object_name: Name of the astronomical object (e.g., 'M31', 'NGC1234')
        ra: Right Ascension in decimal degrees
        dec: Declination in decimal degrees
        wavelength: Wavelength category for catalog filtering
                   (Radio, IR, Optical, UV, EUV, X-Ray, Gamma, or None for all)
        radius_arcmin: Search radius in arcminutes (default: 2.0)
        output_format: Output format (json, votable, csv, tsv)

    Returns:
        str: The constructed URL for the VizieR TAP API call

    Raises:
        ValueError: If neither object_name nor (ra, dec) coordinates are provided,
                   or if ra/dec are not numeric values

    Examples:
        >>> # Search by object name
        >>> url = viser_api(object_name="M31", wavelength="Optical")

        >>> # Search by coordinates
        >>> url = viser_api(ra=10.684, dec=41.269, radius_arcmin=5.0)
    """

    logger.info(f"Starting viser_api function")
    logger.debug(f"Parameters: object_name={object_name}, ra={ra}, dec={dec}, wavelength={wavelength}, radius_arcmin={radius_arcmin}, output_format={output_format}")

    try:
        # VizieR TAP service endpoint
        base_url = "http://tapvizier.u-strasbg.fr/TAPVizieR/tap/sync"
        logger.debug(f"Base URL: {base_url}")
    
        # Validate input parameters
        if ra is not None or dec is not None:
            if ra is None or dec is None:
                logger.warning("Both ra and dec must be provided for coordinate search")
                raise ValueError("Both ra and dec must be provided for coordinate search")
            try:
                ra = float(ra)
                dec = float(dec)
                logger.debug(f"Validated coordinates: ra={ra}, dec={dec}")
            except (ValueError, TypeError):
                logger.warning("RA and DEC must be numeric values (decimal degrees)")
                raise ValueError("RA and DEC must be numeric values (decimal degrees)")

        if not object_name and (ra is None or dec is None):
            logger.warning("Either object_name or both ra and dec coordinates must be provided")
            raise ValueError("Either object_name or both ra and dec coordinates must be provided")

        # Get wavelength-based catalog filtering
        catalog_filter = ""
        if wavelength and wavelength != "NONE" and wavelength != "Select Wavelength":
            catalog_filter = get_wavelength_catalogs(wavelength)
            logger.debug(f"Applied wavelength filter: {catalog_filter}")

        # Build appropriate ADQL query
        if object_name:
            query = build_vizier_object_query(object_name, catalog_filter)
            logger.debug("Built object name query")
        else:
            query = build_vizier_cone_query(ra, dec, radius_arcmin, catalog_filter)
            logger.debug("Built cone search query")

        # Construct final URL with encoded query
        encoded_query = urllib.parse.quote(query)
        final_url = f"{base_url}?REQUEST=doQuery&LANG=ADQL&FORMAT={output_format}&QUERY={encoded_query}"
        logger.debug(f"Final URL: {final_url}")

        return final_url

    except Exception as e:
        logger.warning(f"Error in viser_api function: {str(e)}")
        raise