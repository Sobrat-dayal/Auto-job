"""Repository for persisting AI inference requests, model metadata, and usage analytics."""

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AIInferenceRequestRecord, AIModelRecord, AIRoutingPreferenceRecord


class AIRepository:
    """Async repository managing AI model catalog, inference logs, and usage telemetry."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def record_request(
        self,
        request_id: str,
        task_category: str,
        provider_id: str,
        model_id: str,
        routing_strategy: str,
        status: str,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        total_tokens: int = 0,
        tokens_source: str = "reported",
        estimated_cost_usd: float = 0.0,
        latency_ms: float = 0.0,
        time_to_first_token_ms: float | None = None,
        task_id: str | None = None,
        error_code: str | None = None,
        error_message: str | None = None,
        routing_decision_json: dict[str, Any] | None = None,
        prompt_preview: str | None = None,
    ) -> AIInferenceRequestRecord:
        """Records an inference request execution entry."""
        record = AIInferenceRequestRecord(
            id=request_id,
            task_id=task_id,
            task_category=task_category,
            provider_id=provider_id,
            model_id=model_id,
            routing_strategy=routing_strategy,
            status=status,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            tokens_source=tokens_source,
            estimated_cost_usd=estimated_cost_usd,
            latency_ms=latency_ms,
            time_to_first_token_ms=time_to_first_token_ms,
            error_code=error_code,
            error_message=error_message,
            routing_decision_json=routing_decision_json or {},
            prompt_preview=prompt_preview,
            completed_at=datetime.now(UTC),
        )
        self.session.add(record)
        await self.session.commit()
        await self.session.refresh(record)
        return record

    async def list_requests(
        self,
        limit: int = 50,
        offset: int = 0,
        provider_id: str | None = None,
        status: str | None = None,
        task_category: str | None = None,
    ) -> tuple[list[AIInferenceRequestRecord], int]:
        """Lists inference requests with pagination and filters."""
        query = select(AIInferenceRequestRecord)
        count_query = select(func.count(AIInferenceRequestRecord.id))

        if provider_id:
            query = query.where(AIInferenceRequestRecord.provider_id == provider_id)
            count_query = count_query.where(AIInferenceRequestRecord.provider_id == provider_id)
        if status:
            query = query.where(AIInferenceRequestRecord.status == status)
            count_query = count_query.where(AIInferenceRequestRecord.status == status)
        if task_category:
            query = query.where(AIInferenceRequestRecord.task_category == task_category)
            count_query = count_query.where(AIInferenceRequestRecord.task_category == task_category)

        total_res = await self.session.execute(count_query)
        total = total_res.scalar() or 0

        query = query.order_by(desc(AIInferenceRequestRecord.created_at)).offset(offset).limit(limit)
        result = await self.session.execute(query)
        records = list(result.scalars().all())
        return records, total

    async def get_usage_summary(self, days: int = 30) -> dict[str, Any]:
        """Aggregates usage metrics for analytics."""
        since = datetime.now(UTC) - timedelta(days=days)
        base_filter = AIInferenceRequestRecord.created_at >= since

        # Overall totals
        stmt = select(
            func.count(AIInferenceRequestRecord.id).label("total_requests"),
            func.coalesce(func.sum(AIInferenceRequestRecord.prompt_tokens), 0).label("total_prompt_tokens"),
            func.coalesce(func.sum(AIInferenceRequestRecord.completion_tokens), 0).label("total_completion_tokens"),
            func.coalesce(func.sum(AIInferenceRequestRecord.total_tokens), 0).label("total_tokens"),
            func.coalesce(func.sum(AIInferenceRequestRecord.estimated_cost_usd), 0.0).label("total_cost_usd"),
            func.coalesce(func.avg(AIInferenceRequestRecord.latency_ms), 0.0).label("avg_latency_ms"),
        ).where(base_filter)

        res = await self.session.execute(stmt)
        row = res.one()

        # Success / Failed counts
        status_stmt = (
            select(AIInferenceRequestRecord.status, func.count(AIInferenceRequestRecord.id))
            .where(base_filter)
            .group_by(AIInferenceRequestRecord.status)
        )
        status_res = await self.session.execute(status_stmt)
        status_counts = dict(status_res.all())

        # Provider breakdown
        provider_stmt = (
            select(
                AIInferenceRequestRecord.provider_id,
                func.count(AIInferenceRequestRecord.id).label("requests"),
                func.coalesce(func.sum(AIInferenceRequestRecord.total_tokens), 0).label("tokens"),
                func.coalesce(func.sum(AIInferenceRequestRecord.estimated_cost_usd), 0.0).label("cost"),
            )
            .where(base_filter)
            .group_by(AIInferenceRequestRecord.provider_id)
        )
        provider_res = await self.session.execute(provider_stmt)
        by_provider = [
            {"provider_id": r[0], "requests": r[1], "tokens": r[2], "cost_usd": round(r[3], 4)}
            for r in provider_res.all()
        ]

        # Model breakdown
        model_stmt = (
            select(
                AIInferenceRequestRecord.provider_id,
                AIInferenceRequestRecord.model_id,
                func.count(AIInferenceRequestRecord.id).label("requests"),
                func.coalesce(func.sum(AIInferenceRequestRecord.total_tokens), 0).label("tokens"),
                func.coalesce(func.sum(AIInferenceRequestRecord.estimated_cost_usd), 0.0).label("cost"),
            )
            .where(base_filter)
            .group_by(AIInferenceRequestRecord.provider_id, AIInferenceRequestRecord.model_id)
        )
        model_res = await self.session.execute(model_stmt)
        by_model = [
            {"provider_id": r[0], "model_id": r[1], "requests": r[2], "tokens": r[3], "cost_usd": round(r[4], 4)}
            for r in model_res.all()
        ]

        successful = status_counts.get("completed", 0)
        total = row.total_requests or 0
        success_rate = (successful / total * 100.0) if total > 0 else 100.0

        # Local vs Cloud calculation
        local_requests = sum(p["requests"] for p in by_provider if p["provider_id"] == "ollama")
        cloud_requests = total - local_requests

        return {
            "time_range_days": days,
            "total_requests": total,
            "successful_requests": successful,
            "failed_requests": status_counts.get("failed", 0),
            "cancelled_requests": status_counts.get("cancelled", 0),
            "success_rate_percent": round(success_rate, 2),
            "total_prompt_tokens": row.total_prompt_tokens,
            "total_completion_tokens": row.total_completion_tokens,
            "total_tokens": row.total_tokens,
            "total_estimated_cost_usd": round(row.total_cost_usd, 4),
            "average_latency_ms": round(row.avg_latency_ms, 2),
            "local_requests": local_requests,
            "cloud_requests": cloud_requests,
            "by_provider": by_provider,
            "by_model": by_model,
        }

    async def upsert_models(self, models_data: list[dict[str, Any]]) -> None:
        """Upserts discovered models into the registry cache table."""
        for m in models_data:
            model_record = await self.session.get(AIModelRecord, m["id"])
            if model_record:
                model_record.display_name = m.get("display_name", model_record.display_name)
                model_record.is_available = m.get("is_available", True)
                model_record.context_window = m.get("context_window", model_record.context_window)
                model_record.max_output_tokens = m.get("max_output_tokens", model_record.max_output_tokens)
                model_record.capabilities_json = m.get("capabilities_json", model_record.capabilities_json)
                model_record.pricing_json = m.get("pricing_json", model_record.pricing_json)
                model_record.reported_size_bytes = m.get("reported_size_bytes", model_record.reported_size_bytes)
                model_record.quantization = m.get("quantization", model_record.quantization)
                model_record.status_message = m.get("status_message", model_record.status_message)
                model_record.last_discovered_at = datetime.now(UTC)
            else:
                new_record = AIModelRecord(
                    id=m["id"],
                    provider_id=m["provider_id"],
                    model_id=m["model_id"],
                    display_name=m["display_name"],
                    provider_type=m.get("provider_type", "local"),
                    is_available=m.get("is_available", True),
                    context_window=m.get("context_window", 8192),
                    max_output_tokens=m.get("max_output_tokens", 4096),
                    capabilities_json=m.get("capabilities_json", []),
                    pricing_json=m.get("pricing_json", {}),
                    reported_size_bytes=m.get("reported_size_bytes"),
                    quantization=m.get("quantization"),
                    status_message=m.get("status_message"),
                    last_discovered_at=datetime.now(UTC),
                )
                self.session.add(new_record)
        await self.session.commit()

    async def list_models(self, provider_id: str | None = None) -> list[AIModelRecord]:
        """Lists cached models from the registry table."""
        query = select(AIModelRecord)
        if provider_id:
            query = query.where(AIModelRecord.provider_id == provider_id)
        query = query.order_by(AIModelRecord.provider_id, AIModelRecord.model_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_routing_preferences(self) -> list[AIRoutingPreferenceRecord]:
        """Retrieves all routing preferences."""
        result = await self.session.execute(select(AIRoutingPreferenceRecord))
        return list(result.scalars().all())

    async def upsert_routing_preference(
        self,
        category: str,
        preferred_provider: str,
        preferred_model: str,
        fallback_provider: str | None = None,
        fallback_model: str | None = None,
        is_local_only: bool = False,
    ) -> AIRoutingPreferenceRecord:
        """Upserts a category routing preference."""
        record = await self.session.get(AIRoutingPreferenceRecord, category)
        if record:
            record.preferred_provider = preferred_provider
            record.preferred_model = preferred_model
            record.fallback_provider = fallback_provider
            record.fallback_model = fallback_model
            record.is_local_only = is_local_only
        else:
            record = AIRoutingPreferenceRecord(
                category=category,
                preferred_provider=preferred_provider,
                preferred_model=preferred_model,
                fallback_provider=fallback_provider,
                fallback_model=fallback_model,
                is_local_only=is_local_only,
            )
            self.session.add(record)
        await self.session.commit()
        await self.session.refresh(record)
        return record
