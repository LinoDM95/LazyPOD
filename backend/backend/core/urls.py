from django.urls import path

from .views import (
    AssetUploadView,
    DraftBulkCreateView,
    DraftDetailView,
    DraftListView,
    DraftPushView,
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
]
