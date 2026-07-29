import tempfile
from pathlib import Path

import pytest

from app.ai.documents.filesystem import FilesystemDocumentProvider
from app.ai.interfaces.document import DocumentQuery, DocumentRef


@pytest.mark.asyncio
async def test_fetch_markdown_file_from_filesystem_provider():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        doc = root / "guide.md"
        doc.write_text("# Atlas\n\nKnowledge base.", encoding="utf-8")

        provider = FilesystemDocumentProvider(config={"root": str(root)})
        await provider.initialize()

        refs = await provider.list_documents(DocumentQuery())
        assert any(r.name == "guide.md" for r in refs)

        content = await provider.fetch(DocumentRef(id="1", name="guide.md", uri=str(doc), mime_type="text/markdown"))
        assert "Knowledge base" in (content.text or "")


@pytest.mark.asyncio
async def test_fetch_pdf_file_from_filesystem_provider():
    pypdf = pytest.importorskip("pypdf")
    PdfWriter = pypdf.PdfWriter

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        pdf = root / "blank.pdf"

        writer = PdfWriter()
        writer.add_blank_page(width=200, height=200)
        with pdf.open("wb") as f:
            writer.write(f)

        provider = FilesystemDocumentProvider(config={"root": str(root)})
        await provider.initialize()

        content = await provider.fetch(DocumentRef(id="2", name="blank.pdf", uri=str(pdf), mime_type="application/pdf"))
        assert content.content
        assert content.text is not None
