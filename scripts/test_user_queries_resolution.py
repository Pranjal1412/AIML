import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.ingestion.ingest import process_and_ingest_file
from backend.retrieval.vector_store import get_vector_store
from backend.api.routes import run_full_pipeline

TEST_QUERIES = [
    "What is the maximum loan duration for borrowing reserve course textbooks at the library?",
    "What happens to a student's institutional cloud storage account upon graduation?",
    "Under what specific circumstances are students permitted to request an incomplete (I) grade?",
    "What is the minimum letter grade required for a transfer course to be accepted for academic credit?",
    "How many days in advance must a student submit a formal petition to register a campus event in the quad?",
    "Can I bring a microwave oven into my dormitory residence hall room?",
    "Is it permitted to appeal a financial aid suspension if the GPA drop was caused by hospitalization?",
    "Am I allowed to use the university logo on commercial t-shirts produced by a student organization?",
    "Could I request a temporary waiver for the lab safety goggles requirement if I wear prescription glasses?",
    "Is it against policy for a professor to change the weight of the final exam two weeks before finals?",
    "What is the average wingspan of a Boeing 747 aircraft?",
    "Who directed the movie Inception?",
    "What is the official university policy regarding cryptocurrency mining in student dormitories?",
    "Who approved the latest revision of this academic code of conduct?",
    "What is the difference between a major and a minor in undergraduate degree programs?"
]

def run_test():
    vs = get_vector_store()
    print(f"Total Chunks in ChromaDB before: {vs.get_document_count()}")
    
    # Ingest the 74-page user uploaded Student Manual 2026-27 (MIT-WPU)
    user_pdf = Path(r"C:\Users\tashu\.gemini\antigravity\brain\2bd717a4-a726-4049-a0d3-d1e1c2850b73\.user_uploaded\media_1790192636279.pdf")
    if user_pdf.exists():
        print(f"Ingesting 74-page PDF {user_pdf.name} into vector store...")
        chunks, doc_meta = process_and_ingest_file(str(user_pdf))
        print(f"Ingested {len(chunks)} chunks!")

    print(f"Total Chunks in ChromaDB after: {vs.get_document_count()}")

    print("=" * 80)
    print("TESTING ALL 15 USER QUERIES ACROSS ALL INGESTED POLICY DOCUMENTS")
    print("=" * 80)

    for idx, q in enumerate(TEST_QUERIES, start=1):
        res = run_full_pipeline(q)
        print(f"\n[{idx}/15] QUERY: \"{q}\"")
        print(f"  -> ROUTING : {res.get('routing_mode')}")
        print(f"  -> STATUS  : {res.get('status')}")
        answer_snippet = res.get('final_answer', '')
        print(f"  -> ANSWER  : {answer_snippet[:220]}...")
        sources = res.get('sources', [])
        if sources:
            print(f"  -> CITATION: [{sources[0].get('doc_title')}] {sources[0].get('section')}")

if __name__ == "__main__":
    run_test()
