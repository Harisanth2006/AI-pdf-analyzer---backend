from django.urls import path
from .views import PDFExtractView, DocumentSearchView, ChromaStatusView, UserDocumentListView

urlpatterns = [
    path("extract-pdf/", PDFExtractView.as_view(), name="extract-pdf"),
    path("list/", UserDocumentListView.as_view(), name="document-list"),
    path("search/", DocumentSearchView.as_view(), name="search-documents"),
    path("status/", ChromaStatusView.as_view(), name="status-cromadb"),
]

