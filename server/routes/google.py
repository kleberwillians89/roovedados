from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, Query

from api_support import (
    _elapsed_ms,
    _log_endpoint_call,
    _log_endpoint_done,
    _log_endpoint_error,
    _pick_client_id,
    _runtime_error_status,
    _started,
    _structured_error_response,
)
from services.ga4_reporting import (
    build_ga4_campaigns_report,
    build_ga4_channels_report,
    build_ga4_events_report,
    build_ga4_report,
    resolve_ga4_report_period,
)
from services.ga4_sync import sync_ga4_for_period
from services.single_tenant import get_roove_ga4_property_id
from services.tenant import resolve_client_id

router = APIRouter(tags=["google"])

GOOGLE_ENDPOINTS = [
    "POST /api/google/ga4/sync",
    "GET /api/google/ga4/report",
    "GET /api/google/ga4/channels",
    "GET /api/google/ga4/campaigns",
    "GET /api/google/ga4/events",
]


async def _ga4_request_context(
    *,
    client_id: str | None,
    x_client_id: str | None,
    authorization: str | None,
) -> tuple[str, str]:
    return await resolve_client_id(_pick_client_id(client_id, x_client_id), authorization), get_roove_ga4_property_id()


@router.post("/api/google/ga4/sync")
async def ga4_sync(
    client_id: str | None = Query(default=None),
    x_client_id: str | None = Header(default=None, alias="X-Client-Id"),
    start: str | None = Query(default=None),
    end: str | None = Query(default=None),
    days: int = Query(default=30, ge=1, le=366),
    authorization: str | None = Header(default=None),
):
    started = _started()
    endpoint = "/api/google/ga4/sync"
    user_for_log = await _log_endpoint_call(
        endpoint=endpoint,
        authorization=authorization,
        x_client_id=x_client_id,
        client_id=client_id,
        days=days,
        start=start,
        end=end,
    )
    try:
        client_id, property_id = await _ga4_request_context(
            client_id=client_id,
            x_client_id=x_client_id,
            authorization=authorization,
        )
        payload = await sync_ga4_for_period(
            client_id=client_id,
            property_id=property_id,
            since=start,
            until=end,
            days=days,
            job_name="ga4_sync_manual",
            trigger_source="manual_api",
            record_job_run=True,
        )
        _log_endpoint_done(
            endpoint=endpoint,
            started=started,
            user_id=user_for_log,
            x_client_id=x_client_id,
            client_id=client_id,
        )
        return payload
    except HTTPException as exc:
        _log_endpoint_error(
            endpoint=endpoint,
            exc=exc,
            user_id=user_for_log,
            x_client_id=x_client_id,
            client_id=client_id,
        )
        return _structured_error_response(
            endpoint=endpoint,
            exc=exc,
            status_code=exc.status_code,
            code="ga4_sync_http_error",
        )
    except RuntimeError as exc:
        _log_endpoint_error(
            endpoint=endpoint,
            exc=exc,
            user_id=user_for_log,
            x_client_id=x_client_id,
            client_id=client_id,
        )
        return _structured_error_response(
            endpoint=endpoint,
            exc=exc,
            status_code=_runtime_error_status(exc),
            code="ga4_sync_runtime_error",
        )
    except Exception as exc:
        _log_endpoint_error(
            endpoint=endpoint,
            exc=exc,
            user_id=user_for_log,
            x_client_id=x_client_id,
            client_id=client_id,
        )
        return _structured_error_response(
            endpoint=endpoint,
            exc=exc,
            status_code=500,
            code="ga4_sync_unexpected_error",
        )


@router.get("/api/google/ga4/report")
async def ga4_report(
    client_id: str | None = Query(default=None),
    x_client_id: str | None = Header(default=None, alias="X-Client-Id"),
    start: str | None = Query(default=None),
    end: str | None = Query(default=None),
    days: int = Query(default=30, ge=1, le=366),
    authorization: str | None = Header(default=None),
):
    started = _started()
    endpoint = "/api/google/ga4/report"
    user_for_log = await _log_endpoint_call(
        endpoint=endpoint,
        authorization=authorization,
        x_client_id=x_client_id,
        client_id=client_id,
        days=days,
        start=start,
        end=end,
    )
    try:
        client_id, property_id = await _ga4_request_context(
            client_id=client_id,
            x_client_id=x_client_id,
            authorization=authorization,
        )
        period = resolve_ga4_report_period(start=start, end=end, days=days)
        payload = await build_ga4_report(
            client_id=client_id,
            property_id=property_id,
            period=period,
        )
        _log_endpoint_done(
            endpoint=endpoint,
            started=started,
            user_id=user_for_log,
            x_client_id=x_client_id,
            client_id=client_id,
        )
        return payload
    except HTTPException as exc:
        _log_endpoint_error(
            endpoint=endpoint,
            exc=exc,
            user_id=user_for_log,
            x_client_id=x_client_id,
            client_id=client_id,
        )
        return _structured_error_response(
            endpoint=endpoint,
            exc=exc,
            status_code=exc.status_code,
            code="ga4_report_http_error",
        )
    except RuntimeError as exc:
        _log_endpoint_error(
            endpoint=endpoint,
            exc=exc,
            user_id=user_for_log,
            x_client_id=x_client_id,
            client_id=client_id,
        )
        return _structured_error_response(
            endpoint=endpoint,
            exc=exc,
            status_code=_runtime_error_status(exc),
            code="ga4_report_runtime_error",
        )
    except Exception as exc:
        _log_endpoint_error(
            endpoint=endpoint,
            exc=exc,
            user_id=user_for_log,
            x_client_id=x_client_id,
            client_id=client_id,
        )
        return _structured_error_response(
            endpoint=endpoint,
            exc=exc,
            status_code=500,
            code="ga4_report_unexpected_error",
        )


@router.get("/api/google/ga4/channels")
async def ga4_channels(
    client_id: str | None = Query(default=None),
    x_client_id: str | None = Header(default=None, alias="X-Client-Id"),
    start: str | None = Query(default=None),
    end: str | None = Query(default=None),
    days: int = Query(default=30, ge=1, le=366),
    authorization: str | None = Header(default=None),
):
    started = _started()
    endpoint = "/api/google/ga4/channels"
    user_for_log = await _log_endpoint_call(
        endpoint=endpoint,
        authorization=authorization,
        x_client_id=x_client_id,
        client_id=client_id,
        days=days,
        start=start,
        end=end,
    )
    try:
        client_id, property_id = await _ga4_request_context(
            client_id=client_id,
            x_client_id=x_client_id,
            authorization=authorization,
        )
        period = resolve_ga4_report_period(start=start, end=end, days=days)
        payload = await build_ga4_channels_report(
            client_id=client_id,
            property_id=property_id,
            period=period,
        )
        _log_endpoint_done(
            endpoint=endpoint,
            started=started,
            user_id=user_for_log,
            x_client_id=x_client_id,
            client_id=client_id,
        )
        return payload
    except HTTPException as exc:
        _log_endpoint_error(
            endpoint=endpoint,
            exc=exc,
            user_id=user_for_log,
            x_client_id=x_client_id,
            client_id=client_id,
        )
        return _structured_error_response(
            endpoint=endpoint,
            exc=exc,
            status_code=exc.status_code,
            code="ga4_channels_http_error",
        )
    except RuntimeError as exc:
        _log_endpoint_error(
            endpoint=endpoint,
            exc=exc,
            user_id=user_for_log,
            x_client_id=x_client_id,
            client_id=client_id,
        )
        return _structured_error_response(
            endpoint=endpoint,
            exc=exc,
            status_code=_runtime_error_status(exc),
            code="ga4_channels_runtime_error",
        )
    except Exception as exc:
        _log_endpoint_error(
            endpoint=endpoint,
            exc=exc,
            user_id=user_for_log,
            x_client_id=x_client_id,
            client_id=client_id,
        )
        return _structured_error_response(
            endpoint=endpoint,
            exc=exc,
            status_code=500,
            code="ga4_channels_unexpected_error",
        )


@router.get("/api/google/ga4/campaigns")
async def ga4_campaigns(
    client_id: str | None = Query(default=None),
    x_client_id: str | None = Header(default=None, alias="X-Client-Id"),
    start: str | None = Query(default=None),
    end: str | None = Query(default=None),
    days: int = Query(default=30, ge=1, le=366),
    authorization: str | None = Header(default=None),
):
    started = _started()
    endpoint = "/api/google/ga4/campaigns"
    user_for_log = await _log_endpoint_call(
        endpoint=endpoint,
        authorization=authorization,
        x_client_id=x_client_id,
        client_id=client_id,
        days=days,
        start=start,
        end=end,
    )
    try:
        client_id, property_id = await _ga4_request_context(
            client_id=client_id,
            x_client_id=x_client_id,
            authorization=authorization,
        )
        period = resolve_ga4_report_period(start=start, end=end, days=days)
        payload = await build_ga4_campaigns_report(
            client_id=client_id,
            property_id=property_id,
            period=period,
        )
        _log_endpoint_done(
            endpoint=endpoint,
            started=started,
            user_id=user_for_log,
            x_client_id=x_client_id,
            client_id=client_id,
        )
        return payload
    except HTTPException as exc:
        _log_endpoint_error(
            endpoint=endpoint,
            exc=exc,
            user_id=user_for_log,
            x_client_id=x_client_id,
            client_id=client_id,
        )
        return _structured_error_response(
            endpoint=endpoint,
            exc=exc,
            status_code=exc.status_code,
            code="ga4_campaigns_http_error",
        )
    except RuntimeError as exc:
        _log_endpoint_error(
            endpoint=endpoint,
            exc=exc,
            user_id=user_for_log,
            x_client_id=x_client_id,
            client_id=client_id,
        )
        return _structured_error_response(
            endpoint=endpoint,
            exc=exc,
            status_code=_runtime_error_status(exc),
            code="ga4_campaigns_runtime_error",
        )
    except Exception as exc:
        _log_endpoint_error(
            endpoint=endpoint,
            exc=exc,
            user_id=user_for_log,
            x_client_id=x_client_id,
            client_id=client_id,
        )
        return _structured_error_response(
            endpoint=endpoint,
            exc=exc,
            status_code=500,
            code="ga4_campaigns_unexpected_error",
        )


@router.get("/api/google/ga4/events")
async def ga4_events(
    client_id: str | None = Query(default=None),
    x_client_id: str | None = Header(default=None, alias="X-Client-Id"),
    start: str | None = Query(default=None),
    end: str | None = Query(default=None),
    days: int = Query(default=30, ge=1, le=366),
    authorization: str | None = Header(default=None),
):
    started = _started()
    endpoint = "/api/google/ga4/events"
    user_for_log = await _log_endpoint_call(
        endpoint=endpoint,
        authorization=authorization,
        x_client_id=x_client_id,
        client_id=client_id,
        days=days,
        start=start,
        end=end,
    )
    try:
        client_id, property_id = await _ga4_request_context(
            client_id=client_id,
            x_client_id=x_client_id,
            authorization=authorization,
        )
        period = resolve_ga4_report_period(start=start, end=end, days=days)
        payload = await build_ga4_events_report(
            client_id=client_id,
            property_id=property_id,
            period=period,
        )
        _log_endpoint_done(
            endpoint=endpoint,
            started=started,
            user_id=user_for_log,
            x_client_id=x_client_id,
            client_id=client_id,
        )
        return payload
    except HTTPException as exc:
        _log_endpoint_error(
            endpoint=endpoint,
            exc=exc,
            user_id=user_for_log,
            x_client_id=x_client_id,
            client_id=client_id,
        )
        return _structured_error_response(
            endpoint=endpoint,
            exc=exc,
            status_code=exc.status_code,
            code="ga4_events_http_error",
        )
    except RuntimeError as exc:
        _log_endpoint_error(
            endpoint=endpoint,
            exc=exc,
            user_id=user_for_log,
            x_client_id=x_client_id,
            client_id=client_id,
        )
        return _structured_error_response(
            endpoint=endpoint,
            exc=exc,
            status_code=_runtime_error_status(exc),
            code="ga4_events_runtime_error",
        )
    except Exception as exc:
        _log_endpoint_error(
            endpoint=endpoint,
            exc=exc,
            user_id=user_for_log,
            x_client_id=x_client_id,
            client_id=client_id,
        )
        return _structured_error_response(
            endpoint=endpoint,
            exc=exc,
            status_code=500,
            code="ga4_events_unexpected_error",
        )
