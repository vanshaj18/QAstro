import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _decode_redis_hash(data: Dict[Any, Any]) -> Dict[str, Any]:
    decoded: Dict[str, Any] = {}
    for key, value in data.items():
        decoded_key = key.decode() if isinstance(key, bytes) else str(key)
        decoded_value = value.decode() if isinstance(value, bytes) else value
        decoded[decoded_key] = decoded_value
    return decoded


def _wavelength_bin(wavelength_value: Optional[float]) -> Optional[str]:
    if wavelength_value is None:
        return None

    wl = float(wavelength_value)
    if wl < 100:
        return "<100nm"
    if wl < 380:
        return "100-379nm"
    if wl < 750:
        return "380-749nm"
    if wl < 1000:
        return "750-999nm"
    if wl < 10000:
        return "1000-9999nm"
    return ">=10000nm"


async def init_task(redis: Any, task_id: str, telescope: str, sub_api: str) -> None:
    task_key = f"qastro:task:{task_id}"
    timestamp = now_iso()
    await redis.hset(
        task_key,
        mapping={
            "status": "queued",
            "created_at": timestamp,
            "updated_at": timestamp,
            "telescope": telescope,
            "sub_api": sub_api,
        },
    )
    await redis.incr("qastro:analytics:counter:submitted")


async def set_task_processing(redis: Any, task_id: str) -> None:
    await redis.hset(
        f"qastro:task:{task_id}",
        mapping={
            "status": "processing",
            "updated_at": now_iso(),
        },
    )


async def set_task_success(redis: Any, task_id: str, result: Dict[str, Any]) -> None:
    await redis.hset(
        f"qastro:task:{task_id}",
        mapping={
            "status": "success",
            "result": json.dumps(result),
            "updated_at": now_iso(),
        },
    )


async def set_task_failed(redis: Any, task_id: str, error: str) -> None:
    await redis.hset(
        f"qastro:task:{task_id}",
        mapping={
            "status": "failed",
            "error": error,
            "updated_at": now_iso(),
        },
    )


async def mark_processed(redis: Any) -> None:
    await redis.incr("qastro:analytics:counter:processed")


async def mark_failed(redis: Any) -> None:
    await redis.incr("qastro:analytics:counter:failed")


async def update_success_analytics(
    redis: Any, telescope: str, sub_api: str, wavelength_value: Optional[float]
) -> None:
    await redis.incr("qastro:analytics:counter:successful")
    await redis.hincrby("qastro:analytics:categorical:telescope_usage", telescope, 1)
    await redis.hincrby("qastro:analytics:categorical:sub_api_usage", sub_api, 1)

    wl_bin = _wavelength_bin(wavelength_value)
    if wl_bin:
        await redis.hincrby("qastro:analytics:wavelength_bins", wl_bin, 1)


async def get_task_data(redis: Any, task_id: str) -> Optional[Dict[str, Any]]:
    task_raw = await redis.hgetall(f"qastro:task:{task_id}")
    if not task_raw:
        return None

    task = _decode_redis_hash(task_raw)
    if "result" in task:
        try:
            task["result"] = json.loads(task["result"])
        except Exception:
            pass
    return task


async def get_analytics_data(redis: Any) -> Dict[str, Any]:
    counters = {
        "submitted": int((await redis.get("qastro:analytics:counter:submitted")) or 0),
        "processed": int((await redis.get("qastro:analytics:counter:processed")) or 0),
        "successful": int((await redis.get("qastro:analytics:counter:successful")) or 0),
        "failed": int((await redis.get("qastro:analytics:counter:failed")) or 0),
    }

    telescope_usage_raw = await redis.hgetall("qastro:analytics:categorical:telescope_usage")
    sub_api_usage_raw = await redis.hgetall("qastro:analytics:categorical:sub_api_usage")
    wavelength_bins_raw = await redis.hgetall("qastro:analytics:wavelength_bins")

    telescope_usage = {
        (k.decode() if isinstance(k, bytes) else str(k)): int(v)
        for k, v in telescope_usage_raw.items()
    }
    sub_api_usage = {
        (k.decode() if isinstance(k, bytes) else str(k)): int(v)
        for k, v in sub_api_usage_raw.items()
    }
    wavelength_bins = {
        (k.decode() if isinstance(k, bytes) else str(k)): int(v)
        for k, v in wavelength_bins_raw.items()
    }

    return {
        "counters": counters,
        "categorical": {
            "telescope_usage": telescope_usage,
            "sub_api_usage": sub_api_usage,
        },
        "wavelength_bins": wavelength_bins,
    }
