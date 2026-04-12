from typing import List, Dict
from sqlalchemy.dialects.postgresql import insert

from db.session import SessionLocal
from db.models import Job


def upsert_jobs(jobs: List[Dict]) -> int:
    """
    Insert or update jobs in the database using PostgreSQL upsert.

    Returns:
        int: number of rows affected
    """
    if not jobs:
        return 0

    session = SessionLocal()

    try:
        stmt = insert(Job).values(jobs)

        # On conflict (duplicate URL), do nothing
        stmt = stmt.on_conflict_do_nothing(
            index_elements=["url"]
        )

        result = session.execute(stmt)
        session.commit()

        return result.rowcount or 0

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()

from sqlalchemy import select


def get_jobs(limit: int = 10):
    """
    Fetch jobs from the database.
    """
    session = SessionLocal()

    try:
        stmt = select(Job).limit(limit)
        result = session.execute(stmt)

        return [row[0] for row in result.fetchall()]

    finally:
        session.close()