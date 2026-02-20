from rest_framework import serializers

from .models import DesignAsset, ProductDraft, ShopifyProduct, Template


class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = ["id", "name", "gelato_template_id", "metadata", "is_active"]


class DesignAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignAsset
        fields = ["id", "file", "original_filename", "mime_type", "size_bytes", "created_at"]


class ProductDraftSerializer(serializers.ModelSerializer):
    assets = DesignAssetSerializer(many=True, read_only=True)
    template = TemplateSerializer(read_only=True)

    class Meta:
        model = ProductDraft
        fields = [
            "id",
            "title",
            "description",
            "tags",
            "seo",
            "status",
            "price",
            "template",
            "assets",
            "created_at",
            "updated_at",
        ]


class DraftCreateItemSerializer(serializers.Serializer):
    template_id = serializers.IntegerField()
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(allow_blank=True, required=False)
    tags = serializers.ListField(child=serializers.CharField(), required=False)
    seo = serializers.DictField(required=False)
    price = serializers.DecimalField(max_digits=8, decimal_places=2)
    asset_ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)


class BulkDraftCreateSerializer(serializers.Serializer):
    drafts = DraftCreateItemSerializer(many=True)


class ShopifyProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopifyProduct
        fields = ["id", "shopify_product_id", "payload", "created_at"]


class ShopifyStartSerializer(serializers.Serializer):
    shopDomain = serializers.CharField(max_length=255)
