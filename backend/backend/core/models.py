from django.db import models


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Template(TimestampedModel):
    name = models.CharField(max_length=255)
    gelato_template_id = models.CharField(max_length=120, unique=True)
    metadata = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name


class DesignAsset(TimestampedModel):
    file = models.FileField(upload_to="assets/")
    original_filename = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=100, blank=True)
    size_bytes = models.PositiveIntegerField(default=0)


class ProductDraft(TimestampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        QUEUED = "queued", "Queued"
        PUSHED = "pushed", "Pushed"
        FAILED = "failed", "Failed"

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)
    seo = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    template = models.ForeignKey(Template, on_delete=models.PROTECT, related_name="drafts")
    assets = models.ManyToManyField(DesignAsset, related_name="drafts")


class ShopifyProduct(TimestampedModel):
    draft = models.OneToOneField(ProductDraft, on_delete=models.CASCADE, related_name="shopify_product")
    shopify_product_id = models.CharField(max_length=120, unique=True)
    payload = models.JSONField(default=dict, blank=True)


class JobRun(TimestampedModel):
    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    task_name = models.CharField(max_length=120)
    reference_id = models.CharField(max_length=100)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.QUEUED)
    detail = models.JSONField(default=dict, blank=True)


class IntegrationConnection(TimestampedModel):
    class Provider(models.TextChoices):
        SHOPIFY = "shopify", "Shopify"
        GELATO = "gelato", "Gelato"

    provider = models.CharField(max_length=32, choices=Provider.choices, unique=True)
    encrypted_secret = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    last_error = models.TextField(blank=True)
    last_verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return self.provider
