import random
from dataclasses import dataclass

from django.conf import settings


class ExternalServiceError(Exception):
    pass


@dataclass
class PushResult:
    external_id: str
    payload: dict


class ShopifyAdapter:
    def create_product(self, draft_id: int, title: str) -> PushResult:
        if settings.USE_MOCK_APIS:
            fake_id = f"mock-shopify-{draft_id}-{random.randint(1000,9999)}"
            return PushResult(external_id=fake_id, payload={"title": title, "mode": "mock"})
        raise ExternalServiceError("Real Shopify integration is not configured for this environment.")


class GelatoAdapter:
    def list_templates(self) -> list[dict]:
        if settings.USE_MOCK_APIS:
            return [
                {"gelato_template_id": "gelato-tee-unisex", "name": "Unisex Tee", "metadata": {"category": "apparel"}},
                {"gelato_template_id": "gelato-poster-a3", "name": "Poster A3", "metadata": {"category": "wall-art"}},
            ]
        raise ExternalServiceError("Real Gelato integration is not configured for this environment.")
