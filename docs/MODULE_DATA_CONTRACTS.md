# AUTONOM — Module Data Contracts & REST API Specification (Stage 09)

## 1. Overview

Stage 09 introduces REST API contracts and endpoints for job listings, application attempts, and document artifacts, fully integrated with FastAPI and SQLite repositories.

All endpoints require loopback authentication via Bearer token:
`Authorization: Bearer <local_api_key>`

---

## 2. Jobs API Endpoints

### `GET /api/v1/jobs`

Lists persistent job listings from SQLite.

- **Query Parameters**:
  - `status`: Optional status filter (`active`, `expired`, `closed`, `hidden`)
  - `company`: Optional company name substring filter
  - `limit`: Integer (1–100, default 50)
  - `offset`: Integer (default 0)
- **Response**: `JobListResponse`
  ```json
  {
    "items": [
      {
        "id": "uuid-string",
        "source_id": "uuid-string",
        "external_id": "job-board-id",
        "company": "Acme Robotics",
        "title": "Principal Systems Architect",
        "location": "Remote, USA",
        "employment_type": "full_time",
        "work_arrangement": "remote",
        "salary_range": "$220k - $275k",
        "description": "Full job description text...",
        "requirements": "Key requirements text...",
        "application_url": "https://company.example.com/jobs/123",
        "discovered_at": "2026-11-16T12:00:00Z",
        "last_verified_at": "2026-11-16T14:00:00Z",
        "status": "active"
      }
    ],
    "total": 1,
    "limit": 50,
    "offset": 0
  }
  ```

### `GET /api/v1/jobs/{job_id}`

Retrieves full details of a single job listing. Raises `404` if not found.

---

## 3. Applications API Endpoints

### `GET /api/v1/applications`

Lists persistent job applications from SQLite with historical execution attempts and job metadata.

- **Query Parameters**:
  - `status`: Optional filter (`draft`, `ready`, `submitted`, `rejected`, `interviewing`, `offered`)
  - `profile_id`: Optional applicant profile ID filter
  - `limit`: Integer (1–100, default 50)
  - `offset`: Integer (default 0)
- **Response**: `ApplicationListResponse`
  ```json
  {
    "items": [
      {
        "id": "app-uuid",
        "job_id": "job-uuid",
        "profile_id": "profile-uuid",
        "resume_version_id": "resume-uuid",
        "status": "submitted",
        "submitted_at": "2026-11-16T13:30:00Z",
        "updated_at": "2026-11-16T13:30:00Z",
        "confirmation_ref": "CONF-987654",
        "notes": "Automated filing with personalized cover letter",
        "authorization_ref": "auth-sig-user-1",
        "company": "Acme Robotics",
        "job_title": "Principal Systems Architect",
        "attempts": [
          {
            "id": "attempt-uuid",
            "application_id": "app-uuid",
            "attempted_at": "2026-11-16T13:29:45Z",
            "execution_status": "submitted",
            "failure_category": null,
            "error_summary": null,
            "retry_eligible": false,
            "idempotency_key": "attempt-app-uuid-1"
          }
        ]
      }
    ],
    "total": 1,
    "limit": 50,
    "offset": 0
  }
  ```

### `GET /api/v1/applications/{application_id}`

Retrieves full details and attempt logs of a specific application. Raises `404` if not found.

---

## 4. Artifacts API Endpoints

### `GET /api/v1/artifacts`

Lists persistent artifacts, generated resumes, reports, and binary outputs from SQLite.

- **Query Parameters**:
  - `artifact_type`: Optional type filter (`resume_pdf`, `report`, `document`, `spreadsheet`, `presentation`, `3d_model`, `render`)
  - `limit`: Integer (1–100, default 50)
  - `offset`: Integer (default 0)
- **Response**: `ArtifactListResponse`
  ```json
  {
    "items": [
      {
        "id": "art-uuid",
        "artifact_type": "resume_pdf",
        "storage_path": "vault/resumes/staff_systems_v1.pdf",
        "file_size": 245800,
        "checksum": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "related_task_id": "task-uuid",
        "related_profile_id": "profile-uuid",
        "related_application_id": "app-uuid",
        "retention_class": "permanent",
        "created_at": "2026-11-16T10:00:00Z"
      }
    ],
    "total": 1,
    "limit": 50,
    "offset": 0
  }
  ```

### `GET /api/v1/artifacts/{artifact_id}`

Retrieves metadata of a specific artifact. Raises `404` if not found.
