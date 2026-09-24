import sys
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.ingestion.ingest import process_and_ingest_file
from backend.retrieval.vector_store import get_vector_store


def main():
    sample_dir = BASE_DIR / "data" / "sample_policies"
    if not sample_dir.exists():
        print(f"Sample directory not found at {sample_dir}")
        return

    files = list(sample_dir.glob("*.txt")) + list(sample_dir.glob("*.pdf"))
    print(f"Found {len(files)} sample policy files to ingest...")

    v_store = get_vector_store()

    total_chunks = 0
    for f_path in files:
        print(f"Ingesting: {f_path.name}...")
        try:
            chunks, meta = process_and_ingest_file(f_path)
            v_store.upsert_chunks(chunks)
            total_chunks += len(chunks)
            print(f"  -> Generated {len(chunks)} chunks (Type: {meta['doc_type']})")
        except Exception as e:
            print(f"  -> Error ingesting {f_path.name}: {e}")

    print(f"\n[Demo Data Ingestion] Successfully ingested {total_chunks} total chunks into ChromaDB.")


if __name__ == "__main__":
    main()
