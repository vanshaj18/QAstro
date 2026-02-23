import csv
import io
from typing import Any, Dict

import requests

from core.ads import ads_api, get_ads_headers
from core.gaia import gaia_api
from core.irsa import irsa_api
from core.sdss import sdss_api
from core.simbad import simbad_api


def _parse_response_body(response: requests.Response, telescope: str) -> Dict[str, Any]:
    content_type = response.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            return {"format": "json", "data": response.json()}
        except ValueError:
            pass

    if telescope == "IRSA":
        text = response.text
        try:
            rows = list(csv.reader(io.StringIO(text)))
            headers = rows[0] if rows else []
            return {"format": "csv", "headers": headers, "rows": rows[1:]}
        except Exception:
            return {"format": "text", "data": text}
    return {"format": "text", "data": response.text}


def execute_search(payload: Dict[str, Any]) -> Dict[str, Any]:
    object_name = payload.get("object_name")
    object_name = object_name.strip() if isinstance(object_name, str) and object_name.strip() else None
    ra = payload.get("ra")
    dec = payload.get("dec")
    radius = float(payload.get("search_radius", 0.1))
    telescope = payload["telescope"]
    sub_api = payload.get("wavelength", "NONE")

    if telescope == "SIMBAD":
        url = simbad_api(object_name, ra, dec, None, radius_deg=radius, output_format="json")
        response = requests.get(url, timeout=30)
    elif telescope == "IRSA":
        url = irsa_api(object_name, ra, dec, sub_api, radius=radius, output_format="CSV", use_async=False)
        response = requests.get(url, timeout=30)
    elif telescope == "SDSS":
        url = sdss_api(object_name, ra, dec, sub_api, radius=radius * 60.0, output_format="json")
        response = requests.get(url, timeout=30)
    elif telescope == "GAIA ARCHIVE":
        gaia_db = "dr3" if sub_api == "NONE" else sub_api
        url = gaia_api(object_name, ra, dec, gaia_db, radius=radius, output_format="json")
        response = requests.get(url, timeout=30)
    elif telescope == "NASA ADS":
        url = ads_api(object_name=object_name, output_format="json")
        response = requests.get(url, headers=get_ads_headers(), timeout=30)
    else:
        raise ValueError(f"Unhandled telescope '{telescope}'")

    if response.status_code != 200:
        raise ValueError(f"Upstream service error {response.status_code}: {response.text[:300]}")

    return {
        "status": "success",
        "telescope": telescope,
        "sub_api": sub_api,
        "search_radius": radius,
        "query": {"object_name": object_name, "ra": ra, "dec": dec},
        "result": _parse_response_body(response, telescope),
    }
