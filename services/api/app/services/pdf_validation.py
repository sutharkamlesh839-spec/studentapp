"""Small, dependency-free checks for uploaded PDF payloads.

The browser uses PDF.js/pdf-lib for full parsing. The API still rejects the
common failure mode where a text or HTML response is merely renamed to `.pdf`.
"""


def has_pdf_structure(content: bytes) -> bool:
    """Return whether *content* has the required PDF envelope markers.

    A PDF header alone is not enough: it is possible to upload a plain-text
    file beginning with ``%PDF-`` and have it pass a MIME/signature check. The
    trailer markers below are required by the PDF file format and catch that
    class of invalid uploads without adding a heavyweight parser dependency to
    the API service.
    """

    if not content.startswith(b"%PDF-"):
        return False
    eof_position = content.rfind(b"%%EOF")
    if eof_position < 0 or eof_position < len(content) - 2048:
        return False
    return content.find(b"startxref", 0, eof_position) >= 0
