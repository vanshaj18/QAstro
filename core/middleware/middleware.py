"""
This module handles the cleaning of api response objects and prepares
for visualisation module. 
"""

import requests
from typing import Union, Dict, Any
from core.logger.logger import setup_logger

logger = setup_logger(__name__)

def middleware(data: Union[requests.Response, Dict[str, requests.Response]]) -> Union[requests.Response, Dict[str, Any]]:
    """
    Processes response data and prepares it for visualization module.
    Checks if data is a single response object or a dictionary of database responses.

    Args:
        data: Either a single requests.Response object or a dictionary mapping 
              database names to requests.Response objects.

    Returns:
        - If single response: returns the response object as-is
        - If dict of responses: returns a dictionary mapping database names to 
          processed response data (with text, status_code, etc.)
    """
    logger.debug(f"Starting middleware with data: {data}")
    # Check if data is a single response object
    if isinstance(data, requests.Response):
        # Single response object - return as-is
        return data
    
    # Check if data is a dictionary of response objects
    elif isinstance(data, dict):
        # Dictionary of database names -> response objects
        processed_data = {}
        
        for db_name, response in data.items():
            if isinstance(response, requests.Response):
                # Valid response object
                processed_data[db_name] = {
                    "status": "success" if response.status_code == 200 else "error",
                    "data": response.text,
                    "status_code": response.status_code,
                    "headers": dict(response.headers)
                }
            elif hasattr(response, 'error'):
                # Error response object (from ErrorResponse class)
                processed_data[db_name] = {
                    "status": "error",
                    "error": response.error,
                    "status_code": getattr(response, 'status_code', 500)
                }
            else:
                # Unknown type
                processed_data[db_name] = {
                    "status": "error",
                    "error": f"Unknown response type: {type(response)}",
                    "status_code": 500
                }
        
        logger.debug(f"Middleware processed data: {processed_data}")
        return {
            "data": processed_data,
            "status_code": 200,
            "status": "success"
        }
    
    else:
        logger.warning(f"Middleware received unsupported data type: {type(data)}. Expected requests.Response or Dict[str, requests.Response]")
        raise TypeError(f"Middleware received unsupported data type: {type(data)}. Expected requests.Response or Dict[str, requests.Response]")