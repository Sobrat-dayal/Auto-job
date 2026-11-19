# Job Discovery Agent Integration (Stage 26)

## Specialist Agent Upgrade
The Stage 13 `JobDiscoveryAgent` has been upgraded to interface directly with the Stage 26 `JobDiscoveryService` via the `JobDiscoveryAgentAdapter`.

## Supported Capabilities
Autonomous workflows and supervisor agents invoke `JobDiscoveryAgent.execute_capability` using the following capability IDs:

| Capability ID | Description | Input Parameters | Output |
|---|---|---|---|
| `job.discovery.list_sources` | List active discovery sources | `enabled_only: bool` | `sources: list[dict]` |
| `job.discovery.fetch_source` | Poll a single source for updates | `source_id: str, strategy_id?: str` | Snapshot sync summary |
| `job.discovery.import_url` | Parse a single job URL | `url: str, employer_name?: str, target_role?: str` | Observed posting |
| `job.discovery.import_manual` | Ingest user-provided job text | `title: str, employer_name: str, description: str` | Observed posting |
| `job.discovery.start_task` | Start background discovery run | `source_ids: list[str], strategy_id?: str` | Task ID & status |
| `job.discovery.get_task_status`| Poll execution progress | `task_id: str` | Task record & stats |
| `job.discovery.get_summary` | Discovery engine overview | None | Overview stats dict |

## Supervisor Coordination
During autonomous recruitment workflows, the `SupervisorAgent` can request a discovery sweep across enabled sources, await completion of the background task, and hand off newly observed vacancies to `JobMatchingAgent` (Stage 28) and `ResumeAgent` (Stage 23).
