# Applicant-to-Job Eligibility Evaluation

## 1. 10 Structured Eligibility Outcomes
1. `EligibleAndAligned`: All mandatory requirements satisfied; verified evidence exists; career policy fully respected; high preference alignment (relevance index >= 60.0).
2. `EligibleButLowerPriority`: Mandatory requirements met, but lower preference alignment (relevance index < 60.0).
3. `ConditionallyEligible`: Mandatory prerequisites met through accepted practical experience equivalencies, waivers, or alternative qualifications.
4. `RequiresApplicantReview`: Uncertainty in critical qualification or work authorization requires human clarification.
5. `MissingCriticalInformation`: High-priority job data or applicant facts are undisclosed, preventing reliable assessment.
6. `KnownRequirementNotMet`: Confirmed evidence shows applicant lacks one or more mandatory requirements.
7. `RejectedByHardPolicy`: Prohibited by user's employer blocklist, geographic exclusion, or compensation ceiling.
8. `BlockedByAuthorization`: Legal inability to accept role (unresolvable visa sponsorship refusal or country authorization conflict).
9. `JobUnavailable`: Posting closed, expired, or removed by employer.
10. `MatchEvaluationFailed`: Internal parser or data extraction exception.

## 2. Decision Tree & Precedence
```
                  [Job Active?]
                  /           \
               No              Yes
              /                  \
    [JobUnavailable]    [Hard Policy Passed?]
                         /                  \
                      No                     Yes
                     /                         \
          [RejectedByHardPolicy]     [Mandatory Requirements Met?]
                                     /             |             \
                                 Known Unmet    Unknown     Satisfied
                                    /              |             \
                     [KnownRequirementNotMet]  [RequiresReview]   [Eligible]
```
