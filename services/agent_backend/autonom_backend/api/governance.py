"""Autonomy governance and human-in-the-loop approval endpoints."""

import json
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from autonom_backend.db.database import db_manager

router = APIRouter(prefix="/api/governance", tags=["governance"])


class ApprovalDecisionRequest(BaseModel):
    decision: str  # "approved" or "rejected"
    comments: Optional[str] = None


@router.get("/approvals")
async def list_pending_approvals():
    """Lists all actions awaiting human-in-the-loop approval."""
    async with db_manager.get_connection() as db:
        cursor = await db.execute(
            """
            SELECT id, task_id, agent_id, tier, action_type, target_resource, summary, details_json, created_at, status
            FROM approvals
            WHERE status = 'pending'
            ORDER BY created_at DESC;
            """
        )
        rows = await cursor.fetchall()

        approvals = []
        for r in rows:
            details = {}
            if r["details_json"]:
                try:
                    details = json.loads(r["details_json"])
                except Exception:
                    details = {}

            approvals.append(
                {
                    "id": r["id"],
                    "task_id": r["task_id"],
                    "agent_id": r["agent_id"],
                    "tier": r["tier"],
                    "action_type": r["action_type"],
                    "target_resource": r["target_resource"],
                    "summary": r["summary"],
                    "details": details,
                    "created_at": r["created_at"],
                    "status": r["status"],
                }
            )

        return {"pending_approvals": approvals}


@router.post("/approvals/{approval_id}")
async def resolve_approval(approval_id: str, request: ApprovalDecisionRequest):
    """Submits human user decision for a pending approval."""
    if request.decision not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="Decision must be 'approved' or 'rejected'.")

    async with db_manager.get_connection() as db:
        cursor = await db.execute("SELECT id, status FROM approvals WHERE id = ?;", (approval_id,))
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Approval request not found.")
        if row["status"] != "pending":
            raise HTTPException(status_code=400, detail=f"Approval request is already {row['status']}.")

        await db.execute(
            """
            UPDATE approvals
            SET status = ?, resolved_at = CURRENT_TIMESTAMP, resolved_by = 'user'
            WHERE id = ?;
            """,
            (request.decision, approval_id),
        )
        await db.commit()

    return {
        "approval_id": approval_id,
        "status": request.decision,
    }
