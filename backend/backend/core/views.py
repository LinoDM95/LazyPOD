import urllib.parse

from django.conf import settings
from django.db import transaction
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .integrations import (
    GelatoService,
    IntegrationError,
    IntegrationStore,
    ShopifyService,
    integration_status_payload,
    mark_verified,
)
from .models import DesignAsset, IntegrationConnection, ProductDraft, Template
from .serializers import (
    BulkDraftCreateSerializer,
    DesignAssetSerializer,
    ProductDraftSerializer,
    ShopifyStartSerializer,
    TemplateSerializer,
)
from .services import GelatoAdapter
from .tasks import push_draft_to_shopify


@api_view(["GET"])
def health_view(_request):
    return Response({"status": "ok"})


class TemplateListView(APIView):
    def get(self, _request):
        if settings.USE_MOCK_APIS and not Template.objects.exists():
            for item in GelatoAdapter().list_templates():
                Template.objects.get_or_create(
                    gelato_template_id=item["gelato_template_id"],
                    defaults={"name": item["name"], "metadata": item["metadata"]},
                )
        templates = Template.objects.filter(is_active=True).order_by("id")
        return Response(TemplateSerializer(templates, many=True).data)


class AssetUploadView(APIView):
    def post(self, request):
        files = request.FILES.getlist("files")
        if not files:
            return Response({"detail": "No files uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        created = []
        for uploaded_file in files:
            asset = DesignAsset.objects.create(
                file=uploaded_file,
                original_filename=uploaded_file.name,
                mime_type=uploaded_file.content_type or "application/octet-stream",
                size_bytes=uploaded_file.size,
            )
            created.append(asset)
        return Response(DesignAssetSerializer(created, many=True).data, status=status.HTTP_201_CREATED)


class DraftBulkCreateView(APIView):
    def post(self, request):
        serializer = BulkDraftCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        created = []
        with transaction.atomic():
            for item in serializer.validated_data["drafts"]:
                draft = ProductDraft.objects.create(
                    template_id=item["template_id"],
                    title=item["title"],
                    description=item.get("description", ""),
                    tags=item.get("tags", []),
                    seo=item.get("seo", {}),
                    price=item["price"],
                )
                draft.assets.set(item["asset_ids"])
                created.append(draft)
        return Response(ProductDraftSerializer(created, many=True).data, status=status.HTTP_201_CREATED)


class DraftListView(APIView):
    def get(self, _request):
        drafts = ProductDraft.objects.select_related("template").prefetch_related("assets").order_by("-created_at")
        return Response(ProductDraftSerializer(drafts, many=True).data)


class DraftDetailView(APIView):
    def get(self, _request, draft_id: int):
        draft = ProductDraft.objects.select_related("template").prefetch_related("assets").get(id=draft_id)
        return Response(ProductDraftSerializer(draft).data)


class DraftPushView(APIView):
    def post(self, _request, draft_id: int):
        draft = ProductDraft.objects.get(id=draft_id)
        draft.status = ProductDraft.Status.QUEUED
        draft.save(update_fields=["status", "updated_at"])
        task = push_draft_to_shopify.delay(draft.id)
        return Response({"task_id": task.id, "draft_id": draft.id}, status=status.HTTP_202_ACCEPTED)


class IntegrationsView(APIView):
    def get(self, _request):
        return Response(
            {
                "items": [
                    {
                        "provider": item.provider,
                        "status": item.status,
                        "errorMessage": item.error_message,
                        "metadata": item.metadata,
                    }
                    for item in integration_status_payload()
                ]
            }
        )


class GelatoIntegrationView(APIView):
    def post(self, request):
        api_key = str(request.data.get("apiKey", "")).strip()
        if not api_key:
            return Response({"detail": "API key is required"}, status=status.HTTP_400_BAD_REQUEST)

        connection = IntegrationStore.get_or_create(IntegrationConnection.Provider.GELATO)
        try:
            GelatoService.test_key(api_key)
            IntegrationStore.set_secret(connection, {"apiKey": api_key})
            mark_verified(connection)
            return Response({"ok": True})
        except IntegrationError as exc:
            connection.last_error = str(exc)
            connection.save(update_fields=["last_error", "updated_at"])
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, _request):
        connection = IntegrationStore.get_or_create(IntegrationConnection.Provider.GELATO)
        IntegrationStore.clear(connection)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShopifyStartView(APIView):
    def post(self, request):
        serializer = ShopifyStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            shop_domain = ShopifyService.normalize_shop_domain(serializer.validated_data["shopDomain"])
            callback_url = request.build_absolute_uri("/api/integrations/shopify/callback")
            redirect_url, _state = ShopifyService.create_oauth_redirect(shop_domain, callback_url)
            return Response({"redirectUrl": redirect_url})
        except IntegrationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class ShopifyCallbackView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        params = {key: value for key, value in request.query_params.items()}
        shop = params.get("shop", "")
        state = params.get("state", "")
        code = params.get("code", "")

        if not shop or not state or not code:
            return redirect(f"{settings.APP_URL}/integrations?shopify=error&reason=missing_params")

        try:
            ShopifyService.verify_state(state, shop)
            if not ShopifyService.verify_hmac(params, settings.SHOPIFY_CLIENT_SECRET):
                raise IntegrationError("HMAC check failed")
            access_token = ShopifyService.exchange_token(shop, code)
        except IntegrationError as exc:
            connection = IntegrationStore.get_or_create(IntegrationConnection.Provider.SHOPIFY)
            connection.last_error = str(exc)
            connection.save(update_fields=["last_error", "updated_at"])
            reason = urllib.parse.quote(str(exc))
            return redirect(f"{settings.APP_URL}/integrations?shopify=error&reason={reason}")

        connection = IntegrationStore.get_or_create(IntegrationConnection.Provider.SHOPIFY)
        IntegrationStore.set_secret(connection, {"shop": shop, "accessToken": access_token})
        connection.metadata = {"shopDomain": shop}
        connection.last_error = ""
        connection.save(update_fields=["metadata", "last_error", "updated_at"])
        return redirect(f"{settings.APP_URL}/integrations?shopify=connected")


class ShopifyIntegrationView(APIView):
    def delete(self, _request):
        connection = IntegrationStore.get_or_create(IntegrationConnection.Provider.SHOPIFY)
        IntegrationStore.clear(connection)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShopifyTestView(APIView):
    def post(self, _request):
        connection = IntegrationStore.get_or_create(IntegrationConnection.Provider.SHOPIFY)
        secret = IntegrationStore.get_secret(connection)
        if not secret:
            return Response({"detail": "Shopify is not connected"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            ShopifyService.test_connection(secret["shop"], secret["accessToken"])
            mark_verified(connection)
            return Response({"ok": True})
        except IntegrationError as exc:
            connection.last_error = str(exc)
            connection.save(update_fields=["last_error", "updated_at"])
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
