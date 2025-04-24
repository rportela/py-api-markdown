# markitdown_supported_types.py
EXTENSION_CONTENT_TYPE = {
    # Office & PDF
    "pdf": "application/pdf",  # :contentReference[oaicite:0]{index=0}
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # :contentReference[oaicite:1]{index=1}
    "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",  # :contentReference[oaicite:2]{index=2}
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # :contentReference[oaicite:3]{index=3}
    "xls": "application/vnd.ms-excel",  # :contentReference[oaicite:4]{index=4}
    # Images
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",  # :contentReference[oaicite:5]{index=5}
    # Audio / AV
    "wav": "audio/x-wav",
    "mp3": "audio/mpeg",
    "m4a": "audio/mp4",
    "mp4": "video/mp4",  # :contentReference[oaicite:6]{index=6}
    # Web / Mark-up
    "html": "text/html",
    "htm": "text/html",  # :contentReference[oaicite:7]{index=7}
    "txt": "text/plain",
    "text": "text/plain",  # :contentReference[oaicite:8]{index=8}
    "md": "text/markdown",
    "markdown": "text/markdown",  # :contentReference[oaicite:9]{index=9}
    "json": "application/json",
    "jsonl": "application/json",  # :contentReference[oaicite:10]{index=10}
    "xml": "application/xml",
    # Archives & e-books
    "zip": "application/zip",  # :contentReference[oaicite:11]{index=11}
    "epub": "application/epub+zip",  # :contentReference[oaicite:12]{index=12}
}
