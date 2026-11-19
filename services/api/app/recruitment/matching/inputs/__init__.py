"""Input resolvers for Stage 29 Matching Engine."""

from app.recruitment.matching.inputs.applicant_snapshot import resolve_applicant_snapshot
from app.recruitment.matching.inputs.canonical_jobs import resolve_canonical_job
from app.recruitment.matching.inputs.career_policy import resolve_career_policy
from app.recruitment.matching.inputs.evidence import resolve_evidence_map
from app.recruitment.matching.inputs.job_intelligence import resolve_job_intelligence

__all__ = [
    "resolve_applicant_snapshot",
    "resolve_canonical_job",
    "resolve_job_intelligence",
    "resolve_career_policy",
    "resolve_evidence_map",
]
