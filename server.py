import json
from typing import Any, Dict, List, Optional
from uuid import uuid4

from arq import create_pool
from arq.connections import RedisSettings
from arq.jobs import Job
from fastapi import FastAPI, Header, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="QAstro Privacy-First API", version="3.0.0")
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Use specific methods in production
    allow_headers=["*"], # Use specific headers in production
)

class SearchRequest(BaseModel):
    query: str | None = None
    wavelength: Optional[float] = Field(default=None, gt=0)
    databases: List[str] = Field(default_factory=list)
    include_papers: bool = False


async def _scan_for_job_owner(redis: Any, job_id: str) -> str | None:
    cursor = 0
    pattern = f"qastro:user:*:results:{job_id}"

    while True:
        cursor, keys = await redis.scan(cursor=cursor, match=pattern, count=100)
        for key in keys:
            decoded = key.decode() if isinstance(key, bytes) else str(key)
            parts = decoded.split(":")
            if len(parts) >= 5:
                return parts[2]
        if cursor == 0:
            break
    return None


@app.on_event("startup")
async def startup() -> None:
    app.state.arq_pool = await create_pool(RedisSettings())


@app.on_event("shutdown")
async def shutdown() -> None:
    await app.state.arq_pool.close()


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/useage")
def useage() -> Dict[str, Any]:
    return {
        "status": "success",
        "privacy": "results are namespaced by user",
        "search_endpoint": "POST /search",
        "results_endpoint": "GET /results/{job_id}",
        "analytics_endpoint": "GET /analytics",
        "header_required": "X-User-ID",
    }


@app.post("/search")
async def search(
    payload: SearchRequest,
    x_user_id: str | None = Header(default=None, alias="X-User-ID"),
) -> Dict[str, Any]:
    if not x_user_id:
        raise HTTPException(status_code=400, detail="Missing X-User-ID header.")

    if payload.include_papers and not payload.query:
        raise HTTPException(status_code=400, detail="query is required when include_papers is true.")

    job_id = str(uuid4())

    private_payload = payload.model_dump()
    private_payload["job_id"] = job_id
    private_payload["wavelength"] = payload.wavelength if payload.wavelength is not None else "ALL"

    anonymous_payload = {
        "wavelength": payload.wavelength if payload.wavelength is not None else "ALL",
        "databases": payload.databases,
    }

    await app.state.arq_pool.setex(f"qastro:job_owner:{job_id}", 86400, x_user_id)

    await app.state.arq_pool.enqueue_job(
        "run_private_search",
        x_user_id,
        private_payload,
        _job_id=f"private:{job_id}",
    )
    await app.state.arq_pool.enqueue_job("update_community_analytics", anonymous_payload)

    return {"status": "queued", "job_id": job_id}


@app.get("/results/{job_id}")
async def get_results(
    job_id: str,
    x_user_id: str | None = Header(default=None, alias="X-User-ID"),
) -> Dict[str, Any]:
    if not x_user_id:
        raise HTTPException(status_code=400, detail="Missing X-User-ID header.")

    redis = app.state.arq_pool
    private_key = f"qastro:user:{x_user_id}:results:{job_id}"
    raw = await redis.get(private_key)

    if raw is not None:
        payload = raw.decode() if isinstance(raw, bytes) else raw
        return {"status": "success", "job_id": job_id, "result": json.loads(payload)}

    owner = await redis.get(f"qastro:job_owner:{job_id}")
    if owner is not None:
        owner_id = owner.decode() if isinstance(owner, bytes) else str(owner)
        if owner_id != x_user_id:
            raise HTTPException(status_code=403, detail="Unauthorized for this job_id.")

        job = Job(f"private:{job_id}", redis=redis)
        try:
            job_info = await job.info()
            if job_info is not None:
                return {
                    "status": "processing",
                    "job_id": job_id,
                    "detail": "Result not ready yet.",
                }
        except Exception:
            pass

        raise HTTPException(status_code=404, detail="Result not found.")

    discovered_owner = await _scan_for_job_owner(redis, job_id)
    if discovered_owner and discovered_owner != x_user_id:
        raise HTTPException(status_code=403, detail="Unauthorized for this job_id.")

    raise HTTPException(status_code=404, detail="Result not found.")


@app.get("/analytics")
async def get_analytics() -> Dict[str, Any]:
    redis = app.state.arq_pool
    wl_data = await redis.hgetall("qastro:community:wavelengths")
    db_data = await redis.hgetall("qastro:community:db_usage")

    return {
        "status": "success",
        "wavelengths": {
            (k.decode() if isinstance(k, bytes) else str(k)): int(v)
            for k, v in wl_data.items()
        },
        "databases": {
            (k.decode() if isinstance(k, bytes) else str(k)): int(v)
            for k, v in db_data.items()
        },
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "error_type": "http_error", "detail": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"status": "error", "error_type": "validation_error", "detail": exc.errors()},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"status": "error", "error_type": "internal_error", "detail": str(exc)},
    )
