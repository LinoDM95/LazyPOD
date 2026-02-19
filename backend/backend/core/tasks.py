from celery import shared_task
from django.db import transaction

from .models import JobRun, ProductDraft, ShopifyProduct
from .services import ExternalServiceError, ShopifyAdapter


@shared_task(bind=True, autoretry_for=(ExternalServiceError,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def push_draft_to_shopify(self, draft_id: int) -> str:
    job = JobRun.objects.create(
        task_name="push_draft_to_shopify",
        reference_id=str(draft_id),
        status=JobRun.Status.RUNNING,
    )

    draft = ProductDraft.objects.get(id=draft_id)
    adapter = ShopifyAdapter()
    try:
        result = adapter.create_product(draft_id=draft.id, title=draft.title)
        with transaction.atomic():
            ShopifyProduct.objects.update_or_create(
                draft=draft,
                defaults={
                    "shopify_product_id": result.external_id,
                    "payload": result.payload,
                },
            )
            draft.status = ProductDraft.Status.PUSHED
            draft.save(update_fields=["status", "updated_at"])
        job.status = JobRun.Status.SUCCESS
        job.detail = {"shopify_product_id": result.external_id}
        job.save(update_fields=["status", "detail", "updated_at"])
        return result.external_id
    except Exception as exc:
        draft.status = ProductDraft.Status.FAILED
        draft.save(update_fields=["status", "updated_at"])
        job.status = JobRun.Status.FAILED
        job.detail = {"error": str(exc)}
        job.save(update_fields=["status", "detail", "updated_at"])
        raise
