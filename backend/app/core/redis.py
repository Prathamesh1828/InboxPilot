"""
Centralized Redis connection configuration.

Supports both plain ``redis://`` (local dev) and TLS ``rediss://``
(Render Key-Value, managed Redis) URLs transparently.

All Redis consumers in the application must use either the module-level
``redis_client`` singleton or call ``get_redis_client()`` — never create
their own ``redis.Redis`` instances.
"""

import logging
import ssl as _ssl
from urllib.parse import urlparse

import redis

from app.core.settings import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _is_tls_url(url: str) -> bool:
    """Return True when the Redis URL uses the ``rediss://`` scheme."""
    return urlparse(url).scheme == "rediss"


def _build_redis_kwargs(url: str) -> dict:
    """
    Return extra keyword arguments for ``redis.Redis.from_url`` when
    the URL requires TLS.

    Render's managed Redis (Key-Value) uses internal certificates that
    are not in the default system trust store, so we disable certificate
    verification.  This is safe because the traffic stays within
    Render's private network.

    For plain ``redis://`` URLs an empty dict is returned.
    """
    if not _is_tls_url(url):
        return {}

    # Use the ssl module constant — works across all redis-py versions.
    return {"ssl_cert_reqs": _ssl.CERT_NONE}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_redis_client(*, decode_responses: bool = True) -> redis.Redis:
    """
    Create a new Redis client using the application's configured URL.

    Most callers should use the module-level ``redis_client`` singleton
    instead of calling this function directly.
    """
    extra = _build_redis_kwargs(settings.redis_url)
    client = redis.Redis.from_url(
        settings.redis_url,
        decode_responses=decode_responses,
        **extra,
    )
    logger.info(
        "[REDIS] Client created (tls=%s)",
        _is_tls_url(settings.redis_url),
    )
    return client


def get_celery_ssl_config() -> dict:
    """
    Return Celery-compatible SSL configuration for broker and backend.

    Returns a dict of config keys to apply via ``celery_app.conf.update()``.
    Returns an empty dict when TLS is not used.
    """
    if not _is_tls_url(settings.redis_url):
        return {}

    return {
        "broker_use_ssl": {"ssl_cert_reqs": _ssl.CERT_NONE},
        "redis_backend_transport_options": {"ssl_cert_reqs": _ssl.CERT_NONE},
    }


# ---------------------------------------------------------------------------
# Module-level singleton — backward-compatible with existing imports:
#
#     from app.core.redis import redis_client
# ---------------------------------------------------------------------------

redis_client: redis.Redis = get_redis_client()
