from django.conf import settings
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DesignAsset, ProductDraft, Template
from .serializers import (
    BulkDraftCreateSerializer,
    DesignAssetSerializer,
    ProductDraftSerializer,
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
