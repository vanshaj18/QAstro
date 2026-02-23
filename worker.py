import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any, Dict, List, Union

import requests
from arq.connections import RedisSettings


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _bin_wavelength_100nm(wavelength: float) -> str:
    start = int(wavelength // 100) * 100
    end = start + 99
    return f"{start}-{end}nm"


def _search_arxiv(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    url = "http://export.arxiv.org/api/query"
    response = requests.get(
        url,
        params={"search_query": f"all:{query}", "start": 0, "max_results": max_results},
        timeout=20,
    )
    response.raise_for_status()

    root = ET.fromstring(response.text)
    ns = {"atom": "http://www.w3.org/2005/Atom"}

    papers: List[Dict[str, Any]] = []
    for entry in root.findall("atom:entry", ns):
        title = entry.find("atom:title", ns)
        summary = entry.find("atom:summary", ns)
        published = entry.find("atom:published", ns)
        link = entry.find("atom:id", ns)
        authors = [a.find("atom:name", ns).text for a in entry.findall("atom:author", ns) if a.find("atom:name", ns) is not None]

        papers.append(
            {
                "title": title.text.strip() if title is not None and title.text else "",
                "summary": summary.text.strip() if summary is not None and summary.text else "",
                "published": published.text if published is not None else None,
                "url": link.text if link is not None else None,
                "authors": authors,
            }
        )
    return papers


def _search_tavily(query: str, max_results: int = 5) -> Dict[str, Any]:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return {"status": "skipped", "reason": "TAVILY_API_KEY is not configured."}

    response = requests.post(
        "https://api.tavily.com/search",
        json={
            "api_key": api_key,
            "query": query,
            "max_results": max_results,
        },
        timeout=20,
    )
    response.raise_for_status()
    return {"status": "success", "data": response.json()}


async def update_community_analytics(ctx: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
    redis = ctx["redis"]

    wavelength_input: Union[str, float, int] = payload.get("wavelength", "ALL")
    databases = payload.get("databases", [])

    if wavelength_input == "ALL" or wavelength_input is None:
        wl_bin = "ALL"
    else:
        wl_bin = _bin_wavelength_100nm(float(wavelength_input))
    await redis.hincrby("qastro:community:wavelengths", wl_bin, 1)

    for db in databases:
        await redis.hincrby("qastro:community:db_usage", str(db), 1)

    return {"status": "success", "wavelength_bin": wl_bin}


async def run_private_search(ctx: Dict[str, Any], user_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    redis = ctx["redis"]

    job_id = payload["job_id"]
    include_papers = bool(payload.get("include_papers", False))
    query = payload.get("query")

    result: Dict[str, Any] = {
        "job_id": job_id,
        "created_at": _now_iso(),
        "request": {
            "query": query,
            "wavelength": payload.get("wavelength", "ALL"),
            "databases": payload.get("databases", []),
            "include_papers": include_papers,
        },
        "papers": {
            "arxiv": [],
            "tavily": {"status": "skipped", "reason": "include_papers is false."},
        },
    }

    if include_papers:
        if not query:
            raise ValueError("query is required when include_papers is true")

        arxiv_error = None
        tavily_error = None

        try:
            result["papers"]["arxiv"] = _search_arxiv(query=query)
        except Exception as exc:
            arxiv_error = str(exc)
            result["papers"]["arxiv"] = []

        try:
            result["papers"]["tavily"] = _search_tavily(query=query)
        except Exception as exc:
            tavily_error = str(exc)
            result["papers"]["tavily"] = {"status": "error", "reason": str(exc)}

        if arxiv_error and tavily_error:
            raise ValueError(f"Both paper providers failed: arXiv={arxiv_error}; Tavily={tavily_error}")

    private_key = f"qastro:user:{user_id}:results:{job_id}"
    await redis.setex(private_key, 86400, json.dumps(result))

    return {"status": "success", "key": private_key}


class WorkerSettings:
    functions = [run_private_search, update_community_analytics]
    redis_settings = RedisSettings()
