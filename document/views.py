from pypdf import PdfReader
from pypdf.errors import PdfReadError
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Document
from .serializers import (DocumentSearchSerializer,DocumentSerializer,PDFUploadSerializer,)
from .utils.chunker import chunk_maker
from .utils.embedding import generate_embeddings
from .utils.v_db import collection, save_chunks, search_documents


class PDFExtractView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        serializer = PDFUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uploaded_file = serializer.validated_data["pdf_file"]

        # Save PDF to media/pdfs/ and generate doc.id
        doc = Document.objects.create(
            user=request.user,
            name=uploaded_file.name,
            file=uploaded_file,
        )

        try:
            reader = PdfReader(doc.file.path)
            pages_text = [page.extract_text() or "" for page in reader.pages]
            full_text = "\n".join(pages_text).strip()
        except PdfReadError:
            doc.file.delete(save=False)
            doc.delete()
            return Response(
                {"error": "The uploaded file is corrupted or not a valid PDF."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        chunks = chunk_maker(full_text, chunk_size=300, chunk_overlap=50)
        structured_chunks = [
            {"chunk_id": idx, "text": text}
            for idx, text in enumerate(chunks)
        ]

        em_chunks = generate_embeddings(structured_chunks)
        save_chunks(
            file_id=doc.id,
            user_id=request.user.id,
            filename=doc.name,
            embedded_chunks=em_chunks,
        )

        return Response(
            {
                "document": DocumentSerializer(doc, context={"request": request}).data,
                "page_count": len(reader.pages),
                "total_chunks_saved": len(em_chunks),
                "message": "PDF extracted, embedded, and saved to ChromaDB.",
            },
            status=status.HTTP_201_CREATED,
        )


class UserDocumentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        documents = Document.objects.filter(user=request.user).order_by("-uploaded_at")
        serializer = DocumentSerializer(documents, many=True, context={"request": request})

        return Response(
            {
                "user_id": request.user.id,
                "total_documents": documents.count(),
                "documents": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class DocumentSearchView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def post(self, request, *args, **kwargs):
        serializer = DocumentSearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        matches = search_documents(
            query=serializer.validated_data["query"],
            top_k=serializer.validated_data["top_k"],
            file_id=serializer.validated_data.get("file_id"),
        )

        return Response(
            {
                "query": serializer.validated_data["query"],
                "total_results": len(matches),
                "results": matches,
            },
            status=status.HTTP_200_OK,
        )


class ChromaStatusView(APIView):
    def get(self, request):
        data = collection.peek(limit=10)
        return Response(
            {
                "total_chunks": collection.count(),
                "sample_ids": data["ids"],
                "sample_metadatas": data["metadatas"],
            }
        )
