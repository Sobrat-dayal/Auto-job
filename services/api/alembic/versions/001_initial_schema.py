"""Initial database schema for AUTONOM Stage 04

Revision ID: 001_initial_schema
Revises: None
Create Date: 2026-11-16 20:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. app_settings
    op.create_table(
        'app_settings',
        sa.Column('key', sa.String(length=128), nullable=False),
        sa.Column('value_json', sqlite.JSON(), nullable=False),
        sa.Column('schema_version', sa.Integer(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('scope', sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint('key')
    )

    # 2. applicant_profiles
    op.create_table(
        'applicant_profiles',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('profile_name', sa.String(length=128), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('contact_info_encrypted', sa.Text(), nullable=True),
        sa.Column('education_json', sqlite.JSON(), nullable=True),
        sa.Column('experience_json', sqlite.JSON(), nullable=True),
        sa.Column('career_preferences_json', sqlite.JSON(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. verified_skills
    op.create_table(
        'verified_skills',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('profile_id', sa.String(length=36), nullable=False),
        sa.Column('skill_name', sa.String(length=128), nullable=False),
        sa.Column('category', sa.String(length=64), nullable=False),
        sa.Column('evidence_ref', sa.String(length=256), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('verified_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['profile_id'], ['applicant_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_verified_skills_profile_id', 'verified_skills', ['profile_id'])
    op.create_index('ix_verified_skills_skill_name', 'verified_skills', ['skill_name'])

    # 4. profile_evidence
    op.create_table(
        'profile_evidence',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('profile_id', sa.String(length=36), nullable=False),
        sa.Column('evidence_type', sa.String(length=64), nullable=False),
        sa.Column('project_ref', sa.String(length=256), nullable=True),
        sa.Column('source_info', sa.Text(), nullable=True),
        sa.Column('verification_status', sa.String(length=32), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['profile_id'], ['applicant_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_profile_evidence_profile_id', 'profile_evidence', ['profile_id'])

    # 5. resume_versions
    op.create_table(
        'resume_versions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('profile_id', sa.String(length=36), nullable=False),
        sa.Column('version_tag', sa.String(length=64), nullable=False),
        sa.Column('template_id', sa.String(length=64), nullable=False),
        sa.Column('artifact_ref', sa.String(length=256), nullable=True),
        sa.Column('target_role', sa.String(length=128), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('checksum', sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(['profile_id'], ['applicant_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_resume_versions_profile_id', 'resume_versions', ['profile_id'])

    # 6. job_sources
    op.create_table(
        'job_sources',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('platform_name', sa.String(length=64), nullable=False),
        sa.Column('source_type', sa.String(length=32), nullable=False),
        sa.Column('source_url', sa.String(length=512), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False),
        sa.Column('connector_config_ref', sa.String(length=128), nullable=True),
        sa.Column('last_synced_at', sa.DateTime(), nullable=True),
        sa.Column('error_status', sa.String(length=256), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('source_url')
    )

    # 7. job_listings
    op.create_table(
        'job_listings',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('source_id', sa.String(length=36), nullable=False),
        sa.Column('external_id', sa.String(length=128), nullable=False),
        sa.Column('company', sa.String(length=128), nullable=False),
        sa.Column('title', sa.String(length=256), nullable=False),
        sa.Column('location', sa.String(length=128), nullable=True),
        sa.Column('employment_type', sa.String(length=64), nullable=True),
        sa.Column('work_arrangement', sa.String(length=32), nullable=True),
        sa.Column('salary_range', sa.String(length=128), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('requirements', sa.Text(), nullable=True),
        sa.Column('application_url', sa.String(length=512), nullable=False),
        sa.Column('discovered_at', sa.DateTime(), nullable=False),
        sa.Column('last_verified_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.ForeignKeyConstraint(['source_id'], ['job_sources.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('source_id', 'external_id', name='uq_job_listings_source_external_id')
    )
    op.create_index('ix_job_listings_source_id', 'job_listings', ['source_id'])
    op.create_index('ix_job_listings_company', 'job_listings', ['company'])
    op.create_index('ix_job_listings_title', 'job_listings', ['title'])
    op.create_index('ix_job_listings_discovered_at', 'job_listings', ['discovered_at'])
    op.create_index('ix_job_listings_status', 'job_listings', ['status'])

    # 8. job_matches
    op.create_table(
        'job_matches',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('job_id', sa.String(length=36), nullable=False),
        sa.Column('profile_id', sa.String(length=36), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('matching_factors_json', sqlite.JSON(), nullable=True),
        sa.Column('missing_requirements_json', sqlite.JSON(), nullable=True),
        sa.Column('eligibility_status', sa.String(length=32), nullable=False),
        sa.Column('evaluated_at', sa.DateTime(), nullable=False),
        sa.Column('evaluator_version', sa.String(length=32), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['job_listings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['profile_id'], ['applicant_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_job_matches_job_id', 'job_matches', ['job_id'])
    op.create_index('ix_job_matches_profile_id', 'job_matches', ['profile_id'])
    op.create_index('ix_job_matches_score', 'job_matches', ['score'])

    # 9. applications
    op.create_table(
        'applications',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('job_id', sa.String(length=36), nullable=False),
        sa.Column('profile_id', sa.String(length=36), nullable=False),
        sa.Column('resume_version_id', sa.String(length=36), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('submitted_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('confirmation_ref', sa.String(length=256), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('authorization_ref', sa.String(length=128), nullable=True),
        sa.ForeignKeyConstraint(['job_id'], ['job_listings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['profile_id'], ['applicant_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['resume_version_id'], ['resume_versions.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_applications_job_id', 'applications', ['job_id'])
    op.create_index('ix_applications_profile_id', 'applications', ['profile_id'])
    op.create_index('ix_applications_status', 'applications', ['status'])

    # 10. application_attempts
    op.create_table(
        'application_attempts',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('application_id', sa.String(length=36), nullable=False),
        sa.Column('attempted_at', sa.DateTime(), nullable=False),
        sa.Column('execution_status', sa.String(length=32), nullable=False),
        sa.Column('failure_category', sa.String(length=64), nullable=True),
        sa.Column('error_summary', sa.Text(), nullable=True),
        sa.Column('confirmation_evidence_ref', sa.String(length=256), nullable=True),
        sa.Column('retry_eligible', sa.Boolean(), nullable=False),
        sa.Column('idempotency_key', sa.String(length=128), nullable=False),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('idempotency_key')
    )
    op.create_index('ix_application_attempts_application_id', 'application_attempts', ['application_id'])

    # 11. tasks
    op.create_table(
        'tasks',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('task_type', sa.String(length=64), nullable=False),
        sa.Column('title', sa.String(length=256), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('priority', sa.String(length=16), nullable=False),
        sa.Column('progress', sa.Float(), nullable=False),
        sa.Column('progress_message', sa.String(length=512), nullable=True),
        sa.Column('input_payload_json', sqlite.JSON(), nullable=True),
        sa.Column('output_result_json', sqlite.JSON(), nullable=True),
        sa.Column('owner_context', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('timeout_seconds', sa.Float(), nullable=False),
        sa.Column('retry_count', sa.Integer(), nullable=False),
        sa.Column('correlation_id', sa.String(length=64), nullable=True),
        sa.Column('error_info_json', sqlite.JSON(), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tasks_task_type', 'tasks', ['task_type'])
    op.create_index('ix_tasks_status', 'tasks', ['status'])
    op.create_index('ix_tasks_created_at', 'tasks', ['created_at'])
    op.create_index('ix_tasks_correlation_id', 'tasks', ['correlation_id'])

    # 12. task_events
    op.create_table(
        'task_events',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('task_id', sa.String(length=64), nullable=False),
        sa.Column('event_type', sa.String(length=64), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('state_transition', sa.String(length=64), nullable=True),
        sa.Column('metadata_json', sqlite.JSON(), nullable=True),
        sa.Column('correlation_id', sa.String(length=64), nullable=True),
        sa.Column('sequence_num', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_task_events_task_id', 'task_events', ['task_id'])
    op.create_index('ix_task_events_event_type', 'task_events', ['event_type'])
    op.create_index('ix_task_events_timestamp', 'task_events', ['timestamp'])

    # 13. worker_runs
    op.create_table(
        'worker_runs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('task_id', sa.String(length=64), nullable=False),
        sa.Column('worker_id', sa.String(length=64), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('execution_result_json', sqlite.JSON(), nullable=True),
        sa.Column('failure_class', sa.String(length=128), nullable=True),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_worker_runs_task_id', 'worker_runs', ['task_id'])
    op.create_index('ix_worker_runs_worker_id', 'worker_runs', ['worker_id'])

    # 14. agent_definitions
    op.create_table(
        'agent_definitions',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('role', sa.String(length=128), nullable=False),
        sa.Column('capabilities_json', sqlite.JSON(), nullable=True),
        sa.Column('config_ref', sa.String(length=128), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # 15. artifacts
    op.create_table(
        'artifacts',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('artifact_type', sa.String(length=64), nullable=False),
        sa.Column('storage_path', sa.String(length=512), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('checksum', sa.String(length=64), nullable=False),
        sa.Column('related_task_id', sa.String(length=64), nullable=True),
        sa.Column('related_profile_id', sa.String(length=36), nullable=True),
        sa.Column('related_application_id', sa.String(length=36), nullable=True),
        sa.Column('retention_class', sa.String(length=32), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_artifacts_artifact_type', 'artifacts', ['artifact_type'])
    op.create_index('ix_artifacts_related_task_id', 'artifacts', ['related_task_id'])
    op.create_index('ix_artifacts_related_profile_id', 'artifacts', ['related_profile_id'])
    op.create_index('ix_artifacts_related_application_id', 'artifacts', ['related_application_id'])

    # 16. credential_references
    op.create_table(
        'credential_references',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('provider', sa.String(length=64), nullable=False),
        sa.Column('credential_type', sa.String(length=32), nullable=False),
        sa.Column('windows_cred_identifier', sa.String(length=128), nullable=True),
        sa.Column('encrypted_blob', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_validated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_credential_references_provider', 'credential_references', ['provider'], unique=True)

    # 17. audit_events
    op.create_table(
        'audit_events',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('actor_id', sa.String(length=64), nullable=False),
        sa.Column('action_type', sa.String(length=64), nullable=False),
        sa.Column('resource_type', sa.String(length=64), nullable=False),
        sa.Column('resource_id', sa.String(length=128), nullable=True),
        sa.Column('outcome', sa.String(length=32), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('correlation_id', sa.String(length=64), nullable=True),
        sa.Column('safe_metadata_json', sqlite.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_audit_events_action_type', 'audit_events', ['action_type'])
    op.create_index('ix_audit_events_timestamp', 'audit_events', ['timestamp'])


def downgrade() -> None:
    op.drop_table('audit_events')
    op.drop_table('credential_references')
    op.drop_table('artifacts')
    op.drop_table('agent_definitions')
    op.drop_table('worker_runs')
    op.drop_table('task_events')
    op.drop_table('tasks')
    op.drop_table('application_attempts')
    op.drop_table('applications')
    op.drop_table('job_matches')
    op.drop_table('job_listings')
    op.drop_table('job_sources')
    op.drop_table('resume_versions')
    op.drop_table('profile_evidence')
    op.drop_table('verified_skills')
    op.drop_table('applicant_profiles')
    op.drop_table('app_settings')
