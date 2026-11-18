"""Deterministic Question Classifier & Taxonomy Engine (Stage 24)."""

from __future__ import annotations

import logging
import re
from app.recruitment.writing.contracts import AnswerType, QuestionCategory

logger = logging.getLogger("autonom.recruitment.writing.questions.classification")


class QuestionClassifier:
    """Classifies application questions into standardized recruitment categories and expected answer types."""

    _CATEGORY_PATTERNS: list[tuple[QuestionCategory, list[str]]] = [
        (
            QuestionCategory.ATTESTATION,
            [
                r"\bcertify\b", r"\bconfirm that the above\b", r"\bagree to the terms\b",
                r"\bauthorize a background check\b", r"\bunder penalty of perjury\b",
                r"\baccurate and true\b", r"\backnowledgement\b", r"\bconsent to\b",
            ],
        ),
        (
            QuestionCategory.SENSITIVE_DISCLOSURE,
            [
                r"\bdisability\b", r"\brace\b", r"\bethnicity\b", r"\bgender\b",
                r"\bveteran\b", r"\bprotected characteristic\b", r"\bsexual orientation\b",
                r"\bvoluntary self-identification\b",
            ],
        ),
        (
            QuestionCategory.WORK_ELIGIBILITY,
            [
                r"\bauthorized to work\b", r"\blegally authorized\b", r"\bvisa sponsorship\b",
                r"\bwork permit\b", r"\brequire sponsorship\b", r"\bright to work\b",
                r"\beligible to work\b", r"\bimmigration status\b",
            ],
        ),
        (
            QuestionCategory.COMPENSATION,
            [
                r"\bsalary\b", r"\bcompensation\b", r"\bhourly rate\b", r"\bstipend\b",
                r"\btarget pay\b", r"\bdesired pay\b",
            ],
        ),
        (
            QuestionCategory.AVAILABILITY,
            [
                r"\bearliest start date\b", r"\bnotice period\b", r"\bwhen can you start\b",
                r"\bavailability to begin\b", r"\bwilling to relocate\b", r"\brelocation\b",
                r"\bhours per week\b",
            ],
        ),
        (
            QuestionCategory.EDUCATION,
            [
                r"\bdegree\b", r"\buniversity\b", r"\bcollege\b", r"\bgpa\b",
                r"\bgraduation date\b", r"\bgraduated\b", r"\bfield of study\b",
                r"\bmajor\b", r"\bcoursework\b", r"\bhighest completed qualification\b",
            ],
        ),
        (
            QuestionCategory.SKILLS,
            [
                r"\bwhich listed technologies\b", r"\bproficient in\b", r"\btechnologies have you used\b",
                r"\bprogramming languages\b", r"\bframeworks\b", r"\btools do you use\b",
            ],
        ),
        (
            QuestionCategory.EXPERIENCE,
            [
                r"\byears of (professional )?experience\b", r"\bprevious employment\b",
                r"\brelevant work experience\b", r"\bcurrent role\b", r"\bpast roles\b",
                r"\bindustry experience\b",
            ],
        ),
        (
            QuestionCategory.PROJECTS,
            [
                r"\bdescribe a (relevant )?project\b", r"\bmost proud of\b", r"\bportfolio project\b",
                r"\bwhat did you implement\b", r"\bpersonal project\b", r"\bopen source\b",
            ],
        ),
        (
            QuestionCategory.BEHAVIORAL,
            [
                r"\btell me about a time\b", r"\bdescribe a situation\b", r"\bhow do you handle\b",
                r"\bconflict with a teammate\b", r"\bdisagreement\b", r"\bteamwork\b",
                r"\bmissed a deadline\b", r"\bchallenging problem\b",
            ],
        ),
        (
            QuestionCategory.MOTIVATION,
            [
                r"\bwhy this role\b", r"\bwhy do you want to work\b", r"\bwhy (our company|this company)\b",
                r"\bwhy should we hire you\b", r"\bwhat interests you\b", r"\bcareer goals\b",
            ],
        ),
        (
            QuestionCategory.TECHNICAL,
            [
                r"\bexplain\b", r"\bhow does .* work\b", r"\bdifference between\b",
                r"\bdatabase normalization\b", r"\brest api\b", r"\btradeoff\b",
                r"\bdebugging methodology\b", r"\barchitectural pattern\b",
            ],
        ),
        (
            QuestionCategory.PORTFOLIO,
            [
                r"\bgithub (profile|url|link)\b", r"\bportfolio (link|url)\b", r"\blinkedin\b",
                r"\bpersonal website\b",
            ],
        ),
        (
            QuestionCategory.REFERENCES,
            [
                r"\breference\b", r"\breferrer\b", r"\bmanager contact\b",
            ],
        ),
        (
            QuestionCategory.CONTACT,
            [
                r"\bphone number\b", r"\bemail address\b", r"\bfull legal name\b",
                r"\bcurrent address\b", r"\bpostal code\b", r"\bcity\b",
            ],
        ),
    ]

    @classmethod
    def classify(cls, question_text: str) -> tuple[QuestionCategory, AnswerType, bool, bool]:
        """Returns (QuestionCategory, AnswerType, is_sensitive, requires_attestation)."""
        lower = question_text.lower()

        # 1. Detect Category
        cat = QuestionCategory.UNKNOWN
        for category, patterns in cls._CATEGORY_PATTERNS:
            if any(re.search(pat, lower) for pat in patterns):
                cat = category
                break

        # 2. Detect Attestation & Sensitivity
        requires_attestation = cat == QuestionCategory.ATTESTATION or any(
            t in lower for t in ["certify", "under penalty", "i confirm", "agree to"]
        )
        is_sensitive = cat in (
            QuestionCategory.SENSITIVE_DISCLOSURE,
            QuestionCategory.WORK_ELIGIBILITY,
            QuestionCategory.COMPENSATION,
        )

        # 3. Detect Answer Type
        ans_type = AnswerType.FREE_TEXT
        if any(term in lower for term in ["how many years", "expected salary", "hourly rate", "number of"]):
            ans_type = AnswerType.NUMERIC
        elif any(term in lower for term in ["when can you start", "graduation date", "start date", "expected completion"]):
            ans_type = AnswerType.DATE
        elif cat == QuestionCategory.WORK_ELIGIBILITY or any(
            term in lower for term in [
                "authorized to work", "will you require", "do you have", "have you worked",
                "do you hold", "yes/no", "are you legally", "sponsorship"
            ]
        ):
            ans_type = AnswerType.BOOLEAN
        elif any(term in lower for term in ["which of the following", "select all that apply", "which listed"]):
            ans_type = AnswerType.MULTIPLE_CHOICE
        elif any(term in lower for term in ["select one", "choose one", "highest qualification"]):
            ans_type = AnswerType.SINGLE_CHOICE
        elif any(term in lower for term in ["describe", "explain", "tell me about", "why do you"]):
            ans_type = AnswerType.PARAGRAPH
        elif any(term in lower for term in ["name", "title", "url", "link"]):
            ans_type = AnswerType.SHORT_TEXT

        return cat, ans_type, is_sensitive, requires_attestation
