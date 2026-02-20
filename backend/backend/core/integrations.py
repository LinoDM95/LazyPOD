import hashlib
import hmac
import json
import secrets
import urllib.parse
import urllib.request
from dataclasses import dataclass

from django.conf import settings
from django.core import signing
from django.core.cache import cache
from django.utils import timezone

from .models import IntegrationConnection

SHOPIFY_STATE_CACHE_PREFIX = "shopify_oauth_state:"
SHOPIFY_STATE_TTL_SECONDS = 600


class IntegrationError(Exception):
    pass


@dataclass
class IntegrationStatus:
    provider: str
    status: str
    error_message: str | None
    metadata: dict


class IntegrationStore:
    signer = signing.Signer(salt="integration-secrets")

    @classmethod
    def get_or_create(cls, provider: str) -> IntegrationConnection:
        connection, _ = IntegrationConnection.objects.get_or_create(provider=provider)
        return connection

    @classmethod
    def set_secret(cls, connection: IntegrationConnection, secret: dict) -> None:
        payload = json.dumps(secret)
        connection.encrypted_secret = cls.signer.sign(payload)
        connection.save(update_fields=["encrypted_secret", "updated_at"])

    @classmethod
    def get_secret(cls, connection: IntegrationConnection) -> dict | None:
        if not connection.encrypted_secret:
            return None
        try:
            payload = cls.signer.unsign(connection.encrypted_secret)
            return json.loads(payload)
        except signing.BadSignature:
            return None

    @staticmethod
    def clear(connection: IntegrationConnection) -> None:
        connection.encrypted_secret = ""
        connection.metadata = {}
        connection.last_error = ""
        connection.last_verified_at = None
        connection.save(update_fields=["encrypted_secret", "metadata", "last_error", "last_verified_at", "updated_at"])


class GelatoService:
    @staticmethod
    def test_key(api_key: str) -> None:
        request = urllib.request.Request(
            "https://product.gelatoapis.com/v3/catalogs",
            headers={"X-API-KEY": api_key, "Accept": "application/json"},
            method="GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=12) as response:
                if response.status >= 400:
                    raise IntegrationError("Invalid API key")
        except Exception as exc:  # noqa: BLE001
            raise IntegrationError("Invalid API key") from exc


class ShopifyService:
    @staticmethod
    def normalize_shop_domain(shop_domain: str) -> str:
        value = shop_domain.strip().lower()
        if not value:
            raise IntegrationError("Shop domain is required")
        if "." not in value:
            value = f"{value}.myshopify.com"
        if not value.endswith(".myshopify.com"):
            raise IntegrationError("Shop must end with .myshopify.com")
        return value

    @staticmethod
    def _build_query_without_hmac(params: dict[str, str]) -> str:
        filtered = {k: v for k, v in params.items() if k not in {"hmac", "signature"}}
        pairs = []
        for key in sorted(filtered.keys()):
            pairs.append(f"{key}={filtered[key]}")
        return "&".join(pairs)

    @staticmethod
    def verify_hmac(params: dict[str, str], client_secret: str) -> bool:
        provided_hmac = params.get("hmac", "")
        message = ShopifyService._build_query_without_hmac(params)
        digest = hmac.new(client_secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).hexdigest()
        return hmac.compare_digest(digest, provided_hmac)

    @staticmethod
    def create_oauth_redirect(shop_domain: str, redirect_uri: str) -> tuple[str, str]:
        state = secrets.token_urlsafe(24)
        cache.set(f"{SHOPIFY_STATE_CACHE_PREFIX}{state}", shop_domain, timeout=SHOPIFY_STATE_TTL_SECONDS)
        query = urllib.parse.urlencode(
            {
                "client_id": settings.SHOPIFY_CLIENT_ID,
                "scope": settings.SHOPIFY_SCOPES,
                "redirect_uri": redirect_uri,
                "state": state,
            }
        )
        auth_url = f"https://{shop_domain}/admin/oauth/authorize?{query}"
        return auth_url, state

    @staticmethod
    def verify_state(state: str, shop: str) -> None:
        cached_shop = cache.get(f"{SHOPIFY_STATE_CACHE_PREFIX}{state}")
        cache.delete(f"{SHOPIFY_STATE_CACHE_PREFIX}{state}")
        if not cached_shop or cached_shop != shop:
            raise IntegrationError("State validation failed")

    @staticmethod
    def exchange_token(shop: str, code: str) -> str:
        payload = urllib.parse.urlencode(
            {
                "client_id": settings.SHOPIFY_CLIENT_ID,
                "client_secret": settings.SHOPIFY_CLIENT_SECRET,
                "code": code,
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            f"https://{shop}/admin/oauth/access_token",
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                body = json.loads(response.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            raise IntegrationError("Token exchange failed") from exc

        token = body.get("access_token")
        if not token:
            raise IntegrationError("Token exchange failed")
        return token

    @staticmethod
    def test_connection(shop: str, access_token: str) -> None:
        request = urllib.request.Request(
            f"https://{shop}/admin/api/2026-01/graphql.json",
            data=json.dumps({"query": "{ shop { name myshopifyDomain } }"}).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "X-Shopify-Access-Token": access_token,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                if response.status >= 400:
                    raise IntegrationError("Shop not reachable")
        except Exception as exc:  # noqa: BLE001
            raise IntegrationError("Shop not reachable") from exc


def integration_status_payload() -> list[IntegrationStatus]:
    providers = [IntegrationConnection.Provider.SHOPIFY, IntegrationConnection.Provider.GELATO]
    payload = []
    for provider in providers:
        connection = IntegrationStore.get_or_create(provider)
        status = "connected" if connection.encrypted_secret else "disconnected"
        if connection.last_error:
            status = "error"
        payload.append(
            IntegrationStatus(
                provider=provider,
                status=status,
                error_message=connection.last_error or None,
                metadata=connection.metadata,
            )
        )
    return payload


def mark_verified(connection: IntegrationConnection) -> None:
    connection.last_verified_at = timezone.now()
    if connection.provider == IntegrationConnection.Provider.GELATO:
        connection.metadata = {**connection.metadata, "lastVerified": connection.last_verified_at.isoformat()}
    connection.last_error = ""
    connection.save(update_fields=["last_verified_at", "metadata", "last_error", "updated_at"])
