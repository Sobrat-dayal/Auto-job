"""Job posting exploration, discovery querying, and status management endpoints."""

from typing import Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel
from autonom_backend.db.database import db_manager

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


class JobCreateRequest(BaseModel):
    title: str
    company: str
    location: str
    remote_type: str = "hybrid"
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    currency: str = "USD"
    url: str
    platform: str
    description: Optional[str] = None
    match_score: float = 0.0


@router.get("")
async def list_jobs(
    query: Optional[str] = None,
    platform: Optional[str] = None,
    status: Optional[str] = None,
    min_match: Optional[float] = None,
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
):
    """Retrieves discovered job postings with filtering and pagination."""
    sql_conditions = ["1=1"]
    sql_params = []

    if query:
        sql_conditions.append("(title LIKE ? OR company LIKE ? OR description LIKE ?)")
        wildcard = f"%{query}%"
        sql_params.extend([wildcard, wildcard, wildcard])

    if platform:
        sql_conditions.append("platform = ?")
        sql_params.append(platform)

    if status:
        sql_conditions.append("status = ?")
        sql_params.append(status)

    if min_match is not None:
        sql_conditions.append("match_score >= ?")
        sql_params.append(min_match)

    where_clause = " AND ".join(sql_conditions)

    async with db_manager.get_connection() as db:
        # Get count
        count_cursor = await db.execute(f"SELECT COUNT(*) FROM jobs WHERE {where_clause};", sql_params)
        count_row = await count_cursor.fetchone()
        total = count_row[0] if count_row else 0

        # Get rows
        fetch_sql = f"""
            SELECT id, external_id, title, company, location, remote_type,
                   salary_min, salary_max, currency, url, platform,
                   match_score, status, posted_date, created_at
            FROM jobs
            WHERE {where_clause}
            ORDER BY match_score DESC, created_at DESC
            LIMIT ? OFFSET ?;
        """
        fetch_params = sql_params + [limit, offset]
        cursor = await db.execute(fetch_sql, fetch_params)
        rows = await cursor.fetchall()

        jobs = []
        for r in rows:
            jobs.append(
                {
                    "id": r["id"],
                    "external_id": r["external_id"],
                    "title": r["title"],
                    "company": r["company"],
                    "location": r["location"],
                    "remote_type": r["remote_type"],
                    "salary_min": r["salary_min"],
                    "salary_max": r["salary_max"],
                    "currency": r["currency"],
                    "url": r["url"],
                    "platform": r["platform"],
                    "match_score": r["match_score"],
                    "status": r["status"],
                    "posted_date": r["posted_date"],
                    "created_at": r["created_at"],
                }
            )

        return {
            "total": total,
            "jobs": jobs,
            "page": (offset // limit) + 1 if limit > 0 else 1,
            "limit": limit,
        }
