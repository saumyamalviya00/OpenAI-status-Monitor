# FastAPI Status Monitor — Project Files

# app/main.py
# FastAPI webhook receiver + optional efficient poller fallback for Statuspage-style APIs.
# Usage:
#   pip install -r requirements.txt
#   copy .env.example -> .env and set values as needed
#   uvicorn app.main:app --host 0.0.0.0 --port 8000

import os
import hmac
import hashlib
import asyncio
import logging
from datetime import datetime
from typing import Optional, Any, Dict
import json

from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import PlainTextResponse
import httpx
from dateutil import parser as dateparser

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Optional Redis for dedup across restarts
REDIS_URL = os.getenv("REDIS_URL")
USE_REDIS = bool(REDIS_URL)
SIGNING_SECRET = os.getenv("SIGNING_SECRET")  # optional: HMAC-SHA256 secret used to verify webhook payloads
ENABLE_POLLER = os.getenv("ENABLE_POLLER", "0") in ("1", "true", "True")
STATUS_SUMMARY_URL = os.getenv("STATUS_SUMMARY_URL", "https://status.openai.com/api/v2/summary.json")
POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "30"))

app = FastAPI(title="Statuspage Webhook Receiver (FastAPI)", version="1.0.0")

# In-memory dedup store (fallback). If Redis enabled, we'll use it instead.
seen_update_ids = set()

# If redis is used, create an async client lazily
redis_client = None
if USE_REDIS:
    try:
        import redis.asyncio as redis
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    except ImportError:
        logger.warning("Redis package not found, falling back to in-memory dedup")
        USE_REDIS = False
    except Exception as e:
        logger.warning(f"Redis client creation failed: {e}, falling back to in-memory dedup")
        USE_REDIS = False


def now_ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


async def is_seen(uid: str) -> bool:
    """Return True if uid already seen; atomic when using Redis."""
    if USE_REDIS:
        return await redis_client.sismember("seen_update_ids", uid)
    return uid in seen_update_ids


async def mark_seen(uid: str, ttl_seconds: int = 7 * 24 * 3600):  # 1 week default TTL
    """Mark an update ID as seen with optional TTL to prevent unbounded growth."""
    if USE_REDIS:
        # Add to set and set TTL on the key
        await redis_client.sadd("seen_update_ids", uid)
        # Set TTL on the entire set (only if not already set)
        ttl = await redis_client.ttl("seen_update_ids")
        if ttl == -1:  # No TTL set
            await redis_client.expire("seen_update_ids", ttl_seconds)
    else:
        seen_update_ids.add(uid)
        # For in-memory, implement simple cleanup if set gets too large
        if len(seen_update_ids) > 10000:
            # Remove oldest half (simple cleanup strategy)
            to_remove = list(seen_update_ids)[:5000]
            seen_update_ids.difference_update(to_remove)
            logger.warning(f"Cleaned up in-memory dedup set, removed {len(to_remove)} entries")


def verify_signature(body_bytes: bytes, header_sig: Optional[str]) -> bool:
    """
    Verify HMAC-SHA256 signature. Supports both plain hex and 'sha256=' prefixed formats.
    Header name can be 'X-Signature' or custom; user should configure provider accordingly.
    """
    if not SIGNING_SECRET:
        # no secret configured: skip verification
        return True
    if not header_sig:
        return False
    
    # Handle both plain hex and sha256= prefixed formats
    signature = header_sig
    if signature.startswith('sha256='):
        signature = signature[7:]  # Remove 'sha256=' prefix
    elif signature.startswith('sha1='):
        # Some providers use SHA1 - log warning but attempt verification
        logger.warning("Received SHA1 signature, but using SHA256 for verification")
        signature = signature[5:]
    
    digest = hmac.new(SIGNING_SECRET.encode(), body_bytes, hashlib.sha256).hexdigest()
    # use compare_digest for timing-safe comparison
    return hmac.compare_digest(digest, signature)


def extract_and_print_from_incident(incident: Dict[str, Any], update_obj: Dict[str, Any], component_map: Dict[str, str] = None):
    """
    Given a statuspage 'incident' object and one of its 'incident_update's,
    print the required lines to console with structured logging.
    """
    # determine uid for dedup
    uid = update_obj.get("id") or f"{incident.get('id')}_{update_obj.get('created_at')}"
    comp_name = None
    
    # prefer explicit affected components if available
    if incident.get("components"):
        # could be a list of component objects or ids
        comp = incident["components"][0]
        if isinstance(comp, dict):
            comp_name = comp.get("name")
        else:
            # Try to resolve component ID using component_map
            comp_id = str(comp)
            if component_map and comp_id in component_map:
                comp_name = component_map[comp_id]
            else:
                comp_name = comp_id
    
    # fallback to incident name
    if not comp_name:
        comp_name = incident.get("name") or "Unknown component"

    body = update_obj.get("body") or update_obj.get("content") or "No update body provided"
    ts = update_obj.get("created_at") or update_obj.get("updated_at") or now_ts()
    try:
        ts_parsed = dateparser.parse(ts).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        ts_parsed = now_ts()
    
    # Console output as required by assignment
    print(f"[{ts_parsed}] Product: {comp_name}")
    print(f"Status: {body}\n")
    
    # Also log structured data for monitoring/debugging
    logger.info("Status update", extra={
        "product": comp_name,
        "status": body,
        "timestamp": ts_parsed,
        "incident_id": incident.get("id"),
        "update_id": update_obj.get("id")
    })
    
    return uid


@app.post("/webhook", response_class=PlainTextResponse)
async def webhook_endpoint(request: Request, x_signature: Optional[str] = Header(None)):
    """
    Receive webhook POST events from status provider.
    If SIGNING_SECRET is configured, provider must send the HMAC hex digest in header 'X-Signature'.
    """
    body_bytes = await request.body()
    # verify signature (if configured)
    if SIGNING_SECRET and not verify_signature(body_bytes, x_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    try:
        payload = await request.json()
    except Exception:
        # try to decode as text: some webhooks send form-encoded payloads
        raw = body_bytes.decode("utf-8", errors="ignore")
        try:
            payload = json.loads(raw)
        except Exception:
            payload = {"raw": raw}

    # handle typical shapes: 'incident', 'component' or direct 'incident_update'
    # We'll attempt to extract all updates and print only new ones.

    # INCIDENT payload
    if "incident" in payload:
        incident = payload["incident"]
        updates = incident.get("incident_updates") or []
        # some webhooks send a single 'incident_update' top-level
        if not updates and payload.get("incident_update"):
            updates = [payload["incident_update"]]
        for u in updates:
            uid = u.get("id") or f"{incident.get('id')}_{u.get('created_at')}"
            if await is_seen(uid):
                continue
            # print and mark
            extract_and_print_from_incident(incident, u)
            await mark_seen(uid)
        return PlainTextResponse("", status_code=204)

    # INCIDENT_UPDATE direct
    if "incident_update" in payload:
        u = payload["incident_update"]
        inc = payload.get("incident", {"name": "Unknown incident"})
        uid = u.get("id") or f"{inc.get('id')}_{u.get('created_at')}"
        if not await is_seen(uid):
            extract_and_print_from_incident(inc, u)
            await mark_seen(uid)
        return PlainTextResponse("", status_code=204)

    # COMPONENT changed
    if "component" in payload:
        comp = payload["component"]
        comp_id = comp.get("id") or comp.get("name")
        uid = f"component_{comp_id}_{comp.get('updated_at') or comp.get('status')}"
        if not await is_seen(uid):
            ts = now_ts()
            name = comp.get("name", "Unknown component")
            status = comp.get("status", "unknown")
            print(f"[{ts}] Product: {name}")
            print(f"Status: Component status changed to: {status}\n")
            logger.info("Component update via webhook", extra={
                "product": name,
                "status": f"Component status changed to: {status}",
                "timestamp": ts,
                "component_id": comp.get("id")
            })
            await mark_seen(uid)
        return PlainTextResponse("", status_code=204)

    # Fallback: print summary or message if present
    # Try to find a message field; otherwise print the payload summary (short)
    message = payload.get("message") or payload.get("text") or None
    uid = None
    if message:
        uid = f"fallback_msg_{hash(message)}"
        if not await is_seen(uid):
            ts = now_ts()
            print(f"[{ts}] Product: Unknown")
            print(f"Status: {message}\n")
            logger.info("Fallback message webhook", extra={
                "product": "Unknown",
                "status": message,
                "timestamp": ts
            })
            await mark_seen(uid)
        return PlainTextResponse("", status_code=204)

    # If nothing recognizable, print a short representation (avoid huge dumps)
    small = json.dumps(payload)[:800]
    uid = f"fallback_raw_{hash(small)}"
    if not await is_seen(uid):
        ts = now_ts()
        print(f"[{ts}] Product: Unknown")
        print(f"Status: {small}\n")
        logger.warning("Unknown webhook payload format", extra={
            "product": "Unknown",
            "status": small,
            "timestamp": ts,
            "payload_preview": small[:200]
        })
        await mark_seen(uid)
    return PlainTextResponse("", status_code=204)


@app.get("/health", response_class=PlainTextResponse)
async def health_check():
    """Health check endpoint for monitoring and service discovery."""
    status = {
        "status": "healthy",
        "redis_enabled": USE_REDIS,
        "poller_enabled": ENABLE_POLLER,
        "uptime": datetime.now().isoformat()
    }
    
    # Test Redis connection if enabled
    if USE_REDIS:
        try:
            await redis_client.ping()
            status["redis_status"] = "connected"
        except Exception as e:
            status["redis_status"] = f"error: {str(e)}"
            status["status"] = "degraded"
    
    return PlainTextResponse(json.dumps(status), status_code=200)


# ---------------------------
# Optional: efficient poller
# ---------------------------
etag: Optional[str] = None
last_modified: Optional[str] = None


async def handle_summary_json(json_data: dict):
    """
    Parse summary.json (common Statuspage format). Print new incident updates and component non-operational statuses.
    """
    try:
        # Build component ID to name mapping
        component_map = {}
        components = json_data.get("components", [])
        for comp in components:
            if comp.get("id") and comp.get("name"):
                component_map[comp["id"]] = comp["name"]
        
        # Process incidents
        incidents = json_data.get("incidents", [])
        for inc in incidents:
            updates = inc.get("incident_updates") or []
            for u in updates:
                uid = u.get("id") or f"{inc.get('id')}_{u.get('created_at')}"
                if await is_seen(uid):
                    continue
                extract_and_print_from_incident(inc, u, component_map)
                await mark_seen(uid)

        # Process non-operational components (only print when changes)
        for comp in components:
            name = comp.get("name")
            status = comp.get("status")
            if status and status != "operational":
                uid = f"component_{comp.get('id')}_{status}"
                if not await is_seen(uid):
                    ts = now_ts()
                    print(f"[{ts}] Product: {name}")
                    print(f"Status: Component status: {status}\n")
                    logger.info("Component status change", extra={
                        "product": name,
                        "status": f"Component status: {status}",
                        "timestamp": ts,
                        "component_id": comp.get("id")
                    })
                    await mark_seen(uid)
    except Exception as e:
        logger.error(f"Error processing summary JSON: {e}", exc_info=True)


async def poller_loop():
    global etag, last_modified
    async with httpx.AsyncClient(timeout=20.0) as client:
        backoff = 1
        while True:
            headers = {}
            if etag:
                headers["If-None-Match"] = etag
            if last_modified:
                headers["If-Modified-Since"] = last_modified
            try:
                r = await client.get(STATUS_SUMMARY_URL, headers=headers)
            except Exception as e:
                logger.error(f"Poll error: {e}. Backing off for {min(300, backoff)} seconds", exc_info=True)
                await asyncio.sleep(min(300, backoff))
                backoff = min(backoff * 2, 300)
                continue

            if r.status_code == 304:
                # no change
                await asyncio.sleep(POLL_INTERVAL_SECONDS)
                continue

            if r.status_code == 200:
                backoff = 1
                etag = r.headers.get("ETag") or etag
                last_modified = r.headers.get("Last-Modified") or last_modified
                try:
                    j = r.json()
                except Exception as e:
                    logger.error(f"JSON parse error: {e}", exc_info=True)
                    await asyncio.sleep(POLL_INTERVAL_SECONDS)
                    continue
                await handle_summary_json(j)
                await asyncio.sleep(POLL_INTERVAL_SECONDS)
                continue

            # unexpected
            logger.warning(f"Unexpected status code {r.status_code}: {r.text[:200]}")
            await asyncio.sleep(60)


@app.on_event("startup")
async def startup_event():
    global USE_REDIS  # Declare global before any usage
    
    # If Redis enabled, test connection
    if USE_REDIS and redis_client:
        try:
            await redis_client.ping()
            logger.info(f"Connected to Redis at {REDIS_URL}")
        except Exception as e:
            logger.error(f"Redis connection error: {e} — falling back to in-memory dedup.", exc_info=True)
            # Set USE_REDIS to False to prevent further Redis operations
            USE_REDIS = False
    
    if ENABLE_POLLER:
        # start poller as a background task
        logger.info(f"Poller enabled. Polling: {STATUS_SUMMARY_URL} every {POLL_INTERVAL_SECONDS}s")
        asyncio.create_task(poller_loop())
    else:
        logger.info("Poller disabled. Waiting for incoming webhooks at /webhook")
    
    logger.info("FastAPI Status Monitor started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    if USE_REDIS:
        await redis_client.close()
