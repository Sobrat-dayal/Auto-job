"""Internal Agent Capabilities for Job Aggregation Engine (Stage 27)."""

from typing import Any, Callable, Dict
from pydantic import BaseModel


class AgentCapability(BaseModel):
    name: str
    description: str
    requires_authorization: bool = False
    required_scope: str = ""


AGGREGATION_AGENT_CAPABILITIES: dict[str, AgentCapability] = {
    "job.aggregate.process_observation": AgentCapability(
        name="job.aggregate.process_observation",
        description="Ingest and aggregate a single discovered job observation into canonical records",
        requires_authorization=True,
        required_scope="recruitment.jobs.canonical.create",
    ),
    "job.aggregate.process_batch": AgentCapability(
        name="job.aggregate.process_batch",
        description="Batch process multiple discovered job observations with duplicate detection",
        requires_authorization=True,
        required_scope="recruitment.jobs.canonical.create",
    ),
    "job.aggregate.list_canonical_jobs": AgentCapability(
        name="job.aggregate.list_canonical_jobs",
        description="List and filter canonical deduplicated job opportunities",
        requires_authorization=False,
        required_scope="recruitment.jobs.canonical.read",
    ),
    "job.aggregate.inspect_canonical_job": AgentCapability(
        name="job.aggregate.inspect_canonical_job",
        description="Get detailed canonical job record with source provenance, locations, and conflicts",
        requires_authorization=False,
        required_scope="recruitment.jobs.canonical.read",
    ),
    "job.aggregate.find_duplicate_candidates": AgentCapability(
        name="job.aggregate.find_duplicate_candidates",
        description="Identify potential duplicate vacancies for a given job posting",
        requires_authorization=False,
        required_scope="recruitment.jobs.canonical.read",
    ),
    "job.aggregate.explain_duplicate_decision": AgentCapability(
        name="job.aggregate.explain_duplicate_decision",
        description="Provide explainable positive and negative evidence for a duplicate assessment",
        requires_authorization=False,
        required_scope="recruitment.jobs.canonical.read",
    ),
    "job.aggregate.get_review_queue": AgentCapability(
        name="job.aggregate.get_review_queue",
        description="List ambiguous duplicate candidates awaiting human operator review",
        requires_authorization=True,
        required_scope="recruitment.jobs.duplicate_review",
    ),
    "job.aggregate.resolve_employer": AgentCapability(
        name="job.aggregate.resolve_employer",
        description="Resolve raw employer string, domain, and ATS board to canonical employer identity",
        requires_authorization=True,
        required_scope="recruitment.employers.resolve",
    ),
    "job.aggregate.get_source_lineage": AgentCapability(
        name="job.aggregate.get_source_lineage",
        description="Retrieve all underlying provider observations for a canonical vacancy",
        requires_authorization=False,
        required_scope="recruitment.jobs.canonical.read",
    ),
    "job.aggregate.get_status": AgentCapability(
        name="job.aggregate.get_status",
        description="Get overall job aggregation engine stats and health indicators",
        requires_authorization=False,
        required_scope="recruitment.jobs.canonical.read",
    ),
    "job.aggregate.merge": AgentCapability(
        name="job.aggregate.merge",
        description="Privileged operation to execute transactional merge between two canonical jobs",
        requires_authorization=True,
        required_scope="recruitment.jobs.merge",
    ),
    "job.aggregate.split": AgentCapability(
        name="job.aggregate.split",
        description="Privileged operation to separate erroneously merged sources into a new canonical job",
        requires_authorization=True,
        required_scope="recruitment.jobs.split",
    ),
    "job.aggregate.confirm_employer_mapping": AgentCapability(
        name="job.aggregate.confirm_employer_mapping",
        description="Privileged operation to correct or confirm an employer identity mapping",
        requires_authorization=True,
        required_scope="recruitment.employers.correct",
    ),
}
