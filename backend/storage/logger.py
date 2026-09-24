import json
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional
from backend.config import settings, BASE_DIR

DB_PATH = BASE_DIR / settings.storage.db_path
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def init_db():
    """Initialize SQLite database for session and trace logging."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS query_sessions (
            session_id TEXT PRIMARY KEY,
            timestamp REAL,
            query TEXT,
            status TEXT,
            action_taken TEXT,
            entropy REAL,
            num_clusters INTEGER,
            top_cluster_mass REAL,
            max_similarity REAL,
            retrieval_rounds INTEGER,
            final_answer TEXT,
            full_trace_json TEXT
        )
    """)
    conn.commit()
    conn.close()


init_db()


def log_query_session(trace_data: Dict[str, Any]) -> str:
    """Log a complete query session to SQLite database."""
    session_id = trace_data.get("session_id", str(uuid.uuid4()))
    timestamp = time.time()
    query = trace_data.get("query", "")
    status = trace_data.get("status", "ANSWERED")
    action_taken = trace_data.get("action_taken", "ANSWER")
    entropy = float(trace_data.get("entropy", 0.0))
    num_clusters = int(trace_data.get("num_clusters", 1))
    top_cluster_mass = float(trace_data.get("top_cluster_mass", 1.0))
    max_sim = float(trace_data.get("max_similarity", 0.0))
    rounds = int(trace_data.get("retrieval_rounds_count", 1))
    final_answer = trace_data.get("final_answer", "")
    full_trace_json = json.dumps(trace_data, indent=2)

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO query_sessions (
                session_id, timestamp, query, status, action_taken,
                entropy, num_clusters, top_cluster_mass, max_similarity,
                retrieval_rounds, final_answer, full_trace_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id, timestamp, query, status, action_taken,
            entropy, num_clusters, top_cluster_mass, max_sim,
            rounds, final_answer, full_trace_json
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[Logger] Error logging query session: {e}")

    return session_id


def get_session_by_id(session_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve full trace blob for a session by ID."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT full_trace_json FROM query_sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        conn.close()
        if row and row[0]:
            return json.loads(row[0])
    except Exception as e:
        print(f"[Logger] Error fetching session {session_id}: {e}")
    return None


def get_all_sessions(limit: int = 50) -> List[Dict[str, Any]]:
    """Get list of recent query sessions."""
    sessions = []
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT session_id, timestamp, query, status, action_taken, entropy, num_clusters, max_similarity
            FROM query_sessions ORDER BY timestamp DESC LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()

        for r in rows:
            sessions.append({
                "session_id": r[0],
                "timestamp": r[1],
                "query": r[2],
                "status": r[3],
                "action_taken": r[4],
                "entropy": r[5],
                "num_clusters": r[6],
                "max_similarity": r[7]
            })
    except Exception as e:
        print(f"[Logger] Error fetching sessions: {e}")
    return sessions
