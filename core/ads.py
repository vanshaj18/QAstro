import urllib.parse
import os
from typing import Optional, Dict, Any

def ads_api(
    object_name: Optional[str] = None,
    bibcode: Optional[str] = None,
    author: Optional[str] = None,
    year_range: Optional[str] = None,
    output_format: str = 'json',
    max_records: int = 50
) -> str:
    """
    The NASA ADS API provides access to bibliographic information for astronomy and physics
    publications. This function builds query URLs following the ADS API v1 specification.
    
    Args:
        object_name (str, optional): Name of astronomical object to search for in publications.
                                   Will search in abstract, title, and keywords fields.
        bibcode (str, optional): ADS bibcode identifier (e.g., '2006ApJ...636L..85S').
                               19-character unique identifier for publications.
        author (str, optional): Author name to search for. Can be last name only or 
                              "Last, First" format.
        year_range (str, optional): Publication year range in format "YYYY-YYYY" 
                                  (e.g., "2020-2023") or single year "YYYY".
        output_format (str, optional): Response format. Defaults to 'json'.
                                     Other options: 'xml', 'bibtex', 'endnote'.
        max_records (int, optional): Maximum number of records to return. Defaults to 50.
                                   ADS API limit is 2000 per request.
    
    Returns:
        str: Complete URL for NASA ADS API query with encoded parameters.
    
    Raises:
        ValueError: If no search parameters are provided or if parameters are invalid.
        
    Examples:
        >>> ads_api(object_name="M31")
        'https://api.adsabs.harvard.edu/v1/search/query?q=object:"M31"&fl=bibcode,title,author,year,abstract,doi,pub&rows=50'
        
        >>> ads_api(bibcode="2006ApJ...636L..85S")
        'https://api.adsabs.harvard.edu/v1/search/query?q=bibcode:2006ApJ...636L..85S&fl=bibcode,title,author,year,abstract,doi,pub&rows=50'
        
        >>> ads_api(author="Smith", year_range="2020-2023")
        'https://api.adsabs.harvard.edu/v1/search/query?q=author:"Smith" AND year:2020-2023&fl=bibcode,title,author,year,abstract,doi,pub&rows=50'
    """
    
    # Base URL for NASA ADS API v1
    base_url = "https://api.adsabs.harvard.edu/v1/search/query"
    
    # Build query components
    query_parts = []
    
    # Object name search - searches in abstract, title, and keywords
    if object_name:
        # Clean and quote the object name for search
        clean_object = object_name.strip()
        query_parts.append(f'object:"{clean_object}"')
    
    # Bibcode search - exact match for publication identifier
    if bibcode:
        # Validate bibcode format (19 characters)
        clean_bibcode = bibcode.strip()
        if len(clean_bibcode) != 19:
            raise ValueError(f"Invalid bibcode format. Expected 19 characters, got {len(clean_bibcode)}")
        query_parts.append(f'bibcode:{clean_bibcode}')
    
    # Author search
    if author:
        clean_author = author.strip()
        query_parts.append(f'author:"{clean_author}"')
    
    # Year range search
    if year_range:
        clean_year_range = year_range.strip()
        # Validate year range format
        if '-' in clean_year_range:
            # Range format: YYYY-YYYY
            try:
                start_year, end_year = clean_year_range.split('-')
                start_year = int(start_year.strip())
                end_year = int(end_year.strip())
                if start_year > end_year:
                    raise ValueError("Start year cannot be greater than end year")
                if start_year < 1800 or end_year > 2030:
                    raise ValueError("Year range should be between 1800 and 2030")
                query_parts.append(f'year:{start_year}-{end_year}')
            except ValueError as e:
                if "invalid literal" in str(e):
                    raise ValueError("Invalid year range format. Use YYYY-YYYY or YYYY")
                raise e
        else:
            # Single year format: YYYY
            try:
                year = int(clean_year_range)
                if year < 1800 or year > 2030:
                    raise ValueError("Year should be between 1800 and 2030")
                query_parts.append(f'year:{year}')
            except ValueError:
                raise ValueError("Invalid year format. Use YYYY or YYYY-YYYY")
    
    # Validate that at least one search parameter is provided
    if not query_parts:
        raise ValueError("At least one search parameter is required: object_name, bibcode, author, or year_range")
    
    # Combine query parts with AND operator
    query = " AND ".join(query_parts)
    
    # Define fields to return in response
    # These are the most commonly needed fields for astronomical research
    fields = [
        'bibcode',      # ADS bibcode identifier
        'title',        # Publication title
        'author',       # Author list
        'year',         # Publication year
        'abstract',     # Abstract text
        'doi',          # Digital Object Identifier
        'pub',          # Publication name/journal
        'citation_count', # Number of citations
        'read_count',   # Number of reads
        'keyword'       # Keywords
    ]
    
    # Validate max_records
    if max_records < 1 or max_records > 2000:
        raise ValueError("max_records must be between 1 and 2000")
    
    # Build query parameters
    params = {
        'q': query,
        'fl': ','.join(fields),
        'rows': str(max_records),
        'sort': 'citation_count desc'  # Sort by citation count (most cited first)
    }
    
    # URL encode the parameters
    query_string = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    
    # Construct final URL
    final_url = f"{base_url}?{query_string}"
    
    return final_url


def get_ads_api_key() -> str:
    """
    Retrieves the NASA ADS API key from environment variables.
    
    The API key should be set in the ADS_API_KEY environment variable.

    Returns:
        str: The ADS API key
        
    Raises:
        ValueError: If the API key is not found in environment variables
    """
    api_key = os.getenv('ADS_API_KEY')
    if not api_key:
        raise ValueError(
            "NASA ADS API key not found. Please set the ADS_API_KEY environment variable. "
            "You can obtain a free API key at: https://ui.adsabs.harvard.edu/user/account/login"
        )
    return api_key


def get_ads_headers() -> Dict[str, str]:
    """
    Constructs the required headers for NASA ADS API requests.
    
    Returns:
        dict: Headers dictionary with Authorization and User-Agent
        
    Raises:
        ValueError: If the API key cannot be retrieved
    """
    api_key = get_ads_api_key()
    return {
        'Authorization': f'Bearer {api_key}',
        'User-Agent': 'QAstro/1.0 (Astronomical Database Query Tool)'
    }


def validate_ads_parameters(object_name: Optional[str] = None,
                          bibcode: Optional[str] = None,
                          author: Optional[str] = None,
                          year_range: Optional[str] = None) -> bool:
    """
    Validates NASA ADS API parameters before making a request.
    
    Args:
        object_name (str, optional): Object name to validate
        bibcode (str, optional): Bibcode to validate
        author (str, optional): Author name to validate
        year_range (str, optional): Year range to validate
        
    Returns:
        bool: True if parameters are valid
        
    Raises:
        ValueError: If any parameter is invalid
    """
    # Check that at least one parameter is provided
    if not any([object_name, bibcode, author, year_range]):
        raise ValueError("At least one search parameter must be provided")
    
    # Validate bibcode format if provided
    if bibcode:
        clean_bibcode = bibcode.strip()
        if len(clean_bibcode) != 19:
            raise ValueError(f"Invalid bibcode format. Expected 19 characters, got {len(clean_bibcode)}")
    
    # Validate year range format if provided
    if year_range:
        clean_year_range = year_range.strip()
        if '-' in clean_year_range:
            try:
                start_year, end_year = clean_year_range.split('-')
                start_year = int(start_year.strip())
                end_year = int(end_year.strip())
                if start_year > end_year:
                    raise ValueError("Start year cannot be greater than end year")
                if start_year < 1800 or end_year > 2030:
                    raise ValueError("Year range should be between 1800 and 2030")
            except ValueError as e:
                if "invalid literal" in str(e):
                    raise ValueError("Invalid year range format. Use YYYY-YYYY or YYYY")
                raise e
        else:
            try:
                year = int(clean_year_range)
                if year < 1800 or year > 2030:
                    raise ValueError("Year should be between 1800 and 2030")
            except ValueError:
                raise ValueError("Invalid year format. Use YYYY or YYYY-YYYY")
    
    return True