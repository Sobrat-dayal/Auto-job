"""Agent swarm querying and task dispatch endpoints."""

import json
import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from autonom_backend.db.database import db_manager

router = APIRouter(prefix="/api/agents", tags=["agents"])


class TaskDispatchRequest(BaseModel):
    task_type: str
    parameters: dict
    priority: Optional[str] = "normal"


@router.get("")
async def list_agents():
    """Returns the live status of all registered agents in the swarm."""
    async with db_manager.get_connection() as db:
        cursor = await db.execute(
            """
            SELECT id, name, role, status, current_task, model, tasks_completed
            FROM agents
            ORDER BY id ASC;
            """
        )
        rows = await cursor.fetchall()

        cursor_tasks = await db.execute(
            """
            SELECT COUNT(*) FROM tasks WHERE status IN ('queued', 'running');
            """
        )
        task_count_row = await cursor_tasks.fetchone()
        active_tasks = task_count_row[0] if task_count_row else 0

        agents = []
        for r in rows:
            agents.append(
                {
                    "id": r["id"],
                    "name": r["name"],
                    "role": r["role"],
                    "status": r["status"],
                    "current_task": r["current_task"],
                    "model": r["model"],
                    "tasks_completed": r["tasks_completed"],
                }
            )

        return {
            "agents": agents,
            "total_active_tasks": active_tasks,
        }


@router.post("/{agent_id}/dispatch")
async def dispatch_task(agent_id: str, request: TaskDispatchRequest):
    """Dispatches a task to a target agent."""
    task_id = f"tsk_{uuid.uuid4().hex[:8]}"

    async with db_manager.get_connection() as db:
        # Verify agent exists
        cursor = await db.execute("SELECT id FROM agents WHERE id = ?;", (agent_id,))
        if not await cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found.")

        # Insert new task
        await db.execute(
            """
            INSERT INTO tasks (id, agent_id, task_type, priority, status, parameters_json)
            VALUES (?, ?, ?, ?, 'queued', ?);
            """,
            (task_id, agent_id, request.task_type, request.priority, json.dumps(request.parameters)),
        )
        await db.commit()

    return {
        "task_id": task_id,
        "status": "queued",
        "assigned_agent": agent_id,
    }
