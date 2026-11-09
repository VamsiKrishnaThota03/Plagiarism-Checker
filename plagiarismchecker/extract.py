"""Extract plain text from uploaded .txt, .docx and .pdf files."""
import io

from django.conf import settings

SUPPORTED_EXTENSIONS = ('.txt', '.docx', '.pdf')


class ExtractionError(ValueError):
    """The upload can't be turned into text; the message is safe to show to users."""


def extract_text(upload):
    name = (upload.name or '').lower()
    if not name.endswith(SUPPORTED_EXTENSIONS):
        raise ExtractionError(f'"{upload.name}" is not a .txt, .docx or .pdf file.')
    if upload.size > settings.MAX_UPLOAD_BYTES:
        raise ExtractionError(f'"{upload.name}" is larger than '
                              f'{settings.MAX_UPLOAD_BYTES // (1024 * 1024)} MB.')
    data = upload.read()
    try:
        if name.endswith('.txt'):
            text = data.decode('utf-8-sig', errors='replace')
        elif name.endswith('.docx'):
            from docx import Document
            text = '\n'.join(p.text for p in Document(io.BytesIO(data)).paragraphs)
        else:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(data))
            text = '\n'.join(page.extract_text() or '' for page in reader.pages)
    except Exception as exc:
        raise ExtractionError(f'Could not read "{upload.name}". Is it a valid file?') from exc
    if not text.strip():
        raise ExtractionError(f'No text found in "{upload.name}".')
    return text
