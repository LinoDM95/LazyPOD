import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from core.models import ProductDraft, Template
from core.tasks import push_draft_to_shopify


@pytest.mark.django_db
def test_health_endpoint():
    client = APIClient()
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.django_db
def test_mock_flow():
    client = APIClient()
    template = Template.objects.create(name="Test", gelato_template_id="gelato-test")

    uploaded = SimpleUploadedFile("design.png", b"img", content_type="image/png")
    response = client.post("/api/assets/upload", {"files": [uploaded]}, format="multipart")
    assert response.status_code == 201
    asset_id = response.json()[0]["id"]

    bulk_payload = {
        "drafts": [
            {
                "template_id": template.id,
                "title": "My Draft",
                "price": "19.99",
                "asset_ids": [asset_id],
                "tags": ["pod"],
            }
        ]
    }
    response = client.post("/api/drafts/bulk", bulk_payload, format="json")
    assert response.status_code == 201
    draft_id = response.json()[0]["id"]

    push_draft_to_shopify(draft_id)
    draft = ProductDraft.objects.get(id=draft_id)
    assert draft.status == ProductDraft.Status.PUSHED
    assert draft.shopify_product.shopify_product_id.startswith("mock-shopify-")
