# Multi-Agent Matching Integration

## 1. 13 Internal Agent Capabilities
The Job Matching Engine registers 13 typed capabilities accessible to specialist recruitment agents:
1. `job.matching.evaluate`: Execute evaluation for a single canonical job.
2. `job.matching.evaluate_batch`: Batch evaluate multiple candidate jobs.
3. `job.matching.get_result`: Retrieve stored evaluation record by ID.
4. `job.matching.get_eligibility`: Retrieve eligibility verdict and condition details.
5. `job.matching.get_requirement_coverage`: Retrieve requirement-by-requirement matrix.
6. `job.matching.get_skill_gaps`: Retrieve identified gaps and remediation advice.
7. `job.matching.get_evidence`: Retrieve evidence snippets cited in evaluation.
8. `job.matching.get_ranking`: Retrieve prioritized opportunity queues and KPI statistics.
9. `job.matching.explain_result`: Retrieve transparent mathematical breakdown and counterfactuals.
10. `job.matching.compare_jobs`: Generate side-by-side comparison matrix.
11. `job.matching.get_review_queue`: Fetch pending human review items.
12. `job.matching.simulate`: Run What-If simulation without state mutation.
13. `job.matching.get_history`: Retrieve historical evaluation revisions.

## 2. Inter-Agent Collaboration Patterns
- **JobMatchingAgent**: Executes evaluations and monitors opportunities.
- **VerificationAgent**: Checks applicant evidence references against claimed qualifications.
- **ResumeAgent**: Consumes `job.matching.get_requirement_coverage` to select optimal portfolio projects for tailoring.
- **WritingAgent**: Utilizes `job.matching.explain_result` to tailor cover letter narratives to confirmed requirement matches.
- **Supervisor**: Monitors overall recruitment pipeline progress and ensures zero submissions without human authorization.
