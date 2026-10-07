import os
import re
import uuid
from pathlib import Path
from typing import List, Dict, Any, Tuple
import pypdf
import pdfplumber

from backend.config import settings, BASE_DIR

RAW_DOCS_DIR = BASE_DIR / "storage" / "raw_docs"
RAW_DOCS_DIR.mkdir(parents=True, exist_ok=True)


def classify_doc_type(text: str, filename: str) -> str:
    """Pre-classify document type using simple keyword/heading heuristics."""
    text_lower = (text[:1000] + " " + filename).lower()

    if "attendance" in text_lower or "absence" in text_lower:
        return "attendance_policy"
    elif "faculty" in text_lower or "teacher" in text_lower or "office hours" in text_lower:
        return "faculty_policy"
    elif "exam" in text_lower or "grading" in text_lower or "cgpa" in text_lower or "probation" in text_lower:
        return "exam_regulation"
    elif "plagiarism" in text_lower or "conduct" in text_lower or "misconduct" in text_lower:
        return "code_of_conduct"
    else:
        return "general_handbook"


def extract_header_metadata(text: str) -> Dict[str, Any]:
    """Extract metadata header block and authorship/committee info if present."""
    metadata = {
        "institution": "Apex Academic University",
        "doc_title": "Academic Policy Document",
        "doc_type": "general_handbook",
        "effective_date": "2025-2026",
        "version": "1.0",
        "doc_authors": None,
        "doc_committee": None
    }

    lines = text.split("\n")[:25]
    for line in lines:
        if ":" in line:
            parts = line.split(":", 1)
            key = parts[0].strip().upper()
            val = parts[1].strip()
            if "DOCUMENT TITLE" in key:
                metadata["doc_title"] = val
            elif "DOCUMENT TYPE" in key:
                metadata["doc_type"] = val
            elif "EFFECTIVE DATE" in key:
                metadata["effective_date"] = val
            elif "VERSION" in key:
                metadata["version"] = val
            elif "INSTITUTION" in key:
                metadata["institution"] = val
            elif any(k in key for k in ["AUTHOR", "DRAFTED BY", "PREPARED BY", "WRITTEN BY"]):
                metadata["doc_authors"] = val
            elif any(k in key for k in ["COMMITTEE", "PANEL", "BOARD", "APPROVED BY"]):
                metadata["doc_committee"] = val

    return metadata


def extract_text_from_file(file_path) -> str:
    """Extract text content from PDF or TXT file using multi-engine extraction (PyMuPDF -> pdfplumber -> RapidOCR ML Engine)."""
    file_path = Path(file_path)
    ext = file_path.suffix.lower()
    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    elif ext == ".pdf":
        extracted_text = []

        # Engine 1: PyMuPDF (fitz) - Native text streams
        try:
            import fitz
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc[page_num]
                txt = page.get_text("text") or ""
                if txt.strip():
                    extracted_text.append(f"\n--- PAGE {page_num + 1} ---\n" + txt)
            full_text = "\n".join(extracted_text).strip()
            if len(full_text) > 100:
                return full_text
        except Exception as e:
            print(f"[Ingest Engine 1 - PyMuPDF Error]: {e}")

        # Engine 2: pdfplumber - Layout text blocks
        try:
            extracted_text = []
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    txt = page.extract_text() or ""
                    if txt.strip():
                        extracted_text.append(f"\n--- PAGE {page_num} ---\n" + txt)
            full_text = "\n".join(extracted_text).strip()
            if len(full_text) > 100:
                return full_text
        except Exception as e:
            print(f"[Ingest Engine 2 - pdfplumber Error]: {e}")

        # Engine 3: RapidOCR Fallback (Pure Machine Learning OCR over Page Pixmaps)
        try:
            import fitz
            from rapidocr_onnxruntime import RapidOCR
            ocr_engine = RapidOCR()

            extracted_text = []
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc[page_num]
                pix = page.get_pixmap(dpi=150)
                img_bytes = pix.tobytes("png")
                result, _ = ocr_engine(img_bytes)
                page_ocr_text = " ".join([line[1] for line in result]) if result else ""
                if page_ocr_text.strip():
                    extracted_text.append(f"\n--- PAGE {page_num + 1} ---\n" + page_ocr_text)

            full_text = "\n".join(extracted_text).strip()
            if len(full_text) > 20:
                return full_text
        except Exception as e:
            print(f"[Ingest Engine 3 - RapidOCR Error]: {e}")

        return "\n".join(extracted_text)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")


def clean_text(text: str) -> str:
    """Clean extracted document text: strip headers/footers, de-hyphenate, normalize whitespace."""
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()


def chunk_document(
    text: str,
    doc_metadata: Dict[str, Any],
    chunk_size: int = 500,
    overlap: int = 75
) -> List[Dict[str, Any]]:
    """
    Split document text into chunks preserving true structural section boundaries.
    Section 4 PDF spec: Uses structural heading regex (e.g. ^\\d+(\\.\\d+)*\\s+[A-Z]).
    If no structural heading is found, stores section: None (displayed as 'General').
    """
    cleaned = clean_text(text)
    lines = cleaned.split("\n")

    chunks = []
    current_chunk_lines = []
    current_section = None  # Section 4 spec: default to None if no structural header
    current_page = 1
    current_word_count = 0

    # Structural heading regex per Section 4 PDF spec
    structural_heading_pattern = re.compile(
        r'^(SECTION\s+\d+[:\s]|[0-9]+(\.[0-9]+)+\s+[A-Z]|CHAPTER\s+[0-9IVX]+|ARTICLE\s+[0-9IVX]+)',
        re.IGNORECASE
    )

    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue

        # Page marker check
        page_match = re.match(r'--- PAGE (\d+) ---', line_str)
        if page_match:
            current_page = int(page_match.group(1))
            continue

        # Structural section header check
        if structural_heading_pattern.match(line_str) and len(line_str) < 120:
            current_section = line_str

        words = line_str.split()
        current_chunk_lines.append(line_str)
        current_word_count += len(words)

        if current_word_count >= chunk_size:
            chunk_text = "\n".join(current_chunk_lines)
            chunk_id = f"chk_{doc_metadata['doc_type']}_{uuid.uuid4().hex[:8]}"

            chunk_meta = {
                "chunk_id": chunk_id,
                "institution": doc_metadata.get("institution", "Apex Academic University"),
                "doc_title": doc_metadata.get("doc_title", doc_metadata.get("source_file")),
                "doc_type": doc_metadata.get("doc_type", "general_handbook"),
                "section": current_section or "General",
                "raw_section": current_section,
                "page": current_page,
                "effective_date": doc_metadata.get("effective_date", "2025-2026"),
                "source_file": doc_metadata.get("source_file"),
                "version": doc_metadata.get("version", "1.0"),
                "doc_authors": doc_metadata.get("doc_authors"),
                "doc_committee": doc_metadata.get("doc_committee")
            }

            chunks.append({
                "chunk_id": chunk_id,
                "text": chunk_text,
                "metadata": chunk_meta
            })

            # Overlap handling
            overlap_words = 0
            overlap_lines = []
            for rev_line in reversed(current_chunk_lines):
                lw_count = len(rev_line.split())
                if overlap_words + lw_count <= overlap:
                    overlap_lines.insert(0, rev_line)
                    overlap_words += lw_count
                else:
                    break

            current_chunk_lines = overlap_lines
            current_word_count = overlap_words

    # Final remaining chunk
    if current_chunk_lines:
        chunk_text = "\n".join(current_chunk_lines)
        if len(chunk_text.split()) >= settings.chunking.min_chunk_len or not chunks:
            chunk_id = f"chk_{doc_metadata['doc_type']}_{uuid.uuid4().hex[:8]}"
            chunk_meta = {
                "chunk_id": chunk_id,
                "institution": doc_metadata.get("institution", "Apex Academic University"),
                "doc_title": doc_metadata.get("doc_title", doc_metadata.get("source_file")),
                "doc_type": doc_metadata.get("doc_type", "general_handbook"),
                "section": current_section or "General",
                "raw_section": current_section,
                "page": current_page,
                "effective_date": doc_metadata.get("effective_date", "2025-2026"),
                "source_file": doc_metadata.get("source_file"),
                "version": doc_metadata.get("version", "1.0"),
                "doc_authors": doc_metadata.get("doc_authors"),
                "doc_committee": doc_metadata.get("doc_committee")
            }
            chunks.append({
                "chunk_id": chunk_id,
                "text": chunk_text,
                "metadata": chunk_meta
            })

    return chunks


def process_and_ingest_file(file_path) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Process a single document file end-to-end and prepare chunk objects."""
    file_path = Path(file_path)
    raw_text = extract_text_from_file(file_path)

    # Safely backup original file without corrupting binary format
    backup_path = RAW_DOCS_DIR / file_path.name
    if file_path.resolve() != backup_path.resolve():
        import shutil
        shutil.copy2(file_path, backup_path)

    # Save extracted text backup
    text_backup = RAW_DOCS_DIR / f"{file_path.stem}_extracted.txt"
    with open(text_backup, "w", encoding="utf-8") as f:
        f.write(raw_text)

    header_meta = extract_header_metadata(raw_text)
    doc_type = header_meta["doc_type"] if header_meta["doc_type"] != "general_handbook" else classify_doc_type(raw_text, file_path.name)

    doc_meta = {
        "institution": header_meta["institution"],
        "doc_title": header_meta["doc_title"],
        "doc_type": doc_type,
        "effective_date": header_meta["effective_date"],
        "version": header_meta["version"],
        "doc_authors": header_meta.get("doc_authors"),
        "doc_committee": header_meta.get("doc_committee"),
        "source_file": file_path.name
    }

    chunks = chunk_document(
        raw_text,
        doc_meta,
        chunk_size=settings.chunking.chunk_size,
        overlap=settings.chunking.chunk_overlap
    )

    # Mandatory Ingestion QA Log per Section 4 PDF spec
    print("=" * 80)
    print(f"[INGESTION QA LOG] File: {file_path.name} | Total Chunks: {len(chunks)}")
    print("-" * 80)
    for c in chunks:
        c_id = c["chunk_id"]
        sec = c["metadata"].get("section", "General")
        page = c["metadata"].get("page", 1)
        preview = c["text"][:80].replace("\n", " ")
        print(f"  [{c_id}] | Sec: '{sec}' | Page: {page} | Preview: '{preview}...'")
    print("=" * 80)

    return chunks, doc_meta
