from django.urls import path

from .views import (
    AssetUploadView,
    DraftBulkCreateView,
    DraftDetailView,
    DraftListView,
    DraftPushView,
    GelatoIntegrationView,
    IntegrationsView,
    ShopifyCallbackView,
    ShopifyIntegrationView,
    ShopifyStartView,
    ShopifyTestView,
    TemplateListView,
    health_view,
)

urlpatterns = [
    path("health", health_view),
    path("templates", TemplateListView.as_view()),
    path("assets/upload", AssetUploadView.as_view()),
    path("drafts/bulk", DraftBulkCreateView.as_view()),
    path("drafts", DraftListView.as_view()),
    path("drafts/<int:draft_id>", DraftDetailView.as_view()),
    path("drafts/<int:draft_id>/push", DraftPushView.as_view()),
    path("integrations", IntegrationsView.as_view()),
    path("integrations/gelato", GelatoIntegrationView.as_view()),
    path("integrations/shopify/start", ShopifyStartView.as_view()),
    path("integrations/shopify/callback", ShopifyCallbackView.as_view()),
    path("integrations/shopify", ShopifyIntegrationView.as_view()),
    path("integrations/shopify/test", ShopifyTestView.as_view()),
]
