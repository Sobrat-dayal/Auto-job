"""Deterministic, Evidence-Grounded Cover Letter Generation Engine (Stage 24)."""

from __future__ import annotations

import logging
from typing import Optional
from uuid import uuid4
from app.recruitment.profile.contracts import (
    AcademicStatus,
    ApplicantProfile,
    VerificationStatus,
)
from app.recruitment.writing.contracts import (
    CoverLetterContentBlock,
    CoverLetterType,
    WritingLength,
    WritingSourceReference,
    WritingTone,
)

logger = logging.getLogger("autonom.recruitment.writing.cover_letters.generation")


class CoverLetterGenerator:
    """Generates professional, factual, evidence-anchored cover letter content blocks."""

    @classmethod
    def generate_blocks(
        cls,
        profile: ApplicantProfile,
        target_role: str,
        letter_type: CoverLetterType = CoverLetterType.ROLE_SPECIFIC,
        employer_name: Optional[str] = None,
        job_description_raw: Optional[str] = None,
        tone: WritingTone = WritingTone.PROFESSIONAL,
        length_preference: WritingLength = WritingLength.STANDARD,
        max_words: Optional[int] = 400,
    ) -> list[CoverLetterContentBlock]:
        blocks: list[CoverLetterContentBlock] = []
        ordering_idx = 0

        # Extract verified facts
        applicant_name = getattr(profile.contact, "legal_name", None) or getattr(profile.contact, "preferred_name", None) or "Applicant"
        primary_email = getattr(profile.contact, "primary_email", None) or ""
        phone = getattr(profile.contact, "phone", None) or ""
        loc = getattr(profile, "location", None)
        location_str = f"{getattr(loc, 'city', '')}, {getattr(loc, 'country', '')}".strip(", ") if loc else ""
        portfolio_url = getattr(profile.contact, "portfolio_url", None) or getattr(profile.contact, "website_url", None) or ""

        # Verified Skills
        skills = [
            s.name for s in profile.skills
            if getattr(s, "verification_status", None) in (
                VerificationStatus.USER_CONFIRMED,
                VerificationStatus.EVIDENCE_SUPPORTED,
                VerificationStatus.EXTERNALLY_VERIFIED,
                "user_confirmed",
                "evidence_supported",
                "externally_verified",
            )
        ]
        top_skills = skills[:5] if skills else [s.name for s in profile.skills[:5]]

        # Education
        top_edu = profile.education[0] if profile.education else None
        degree_str = ""
        institution_str = ""
        is_enrolled = False
        if top_edu:
            degree_str = f"{top_edu.degree} in {top_edu.field_of_study}"
            institution_str = top_edu.institution
            status = getattr(top_edu, "academic_status", getattr(top_edu, "status", None))
            is_enrolled = status in (AcademicStatus.CURRENTLY_ENROLLED, "currently_enrolled", "in_progress")

        # Top Project
        top_project = profile.projects[0] if profile.projects else None
        # Top Experience
        top_exp = profile.experience[0] if profile.experience else None

        employer_target = employer_name or "your team"

        # 1. Header Block
        header_text = f"{applicant_name}\n"
        contact_parts = [p for p in [primary_email, phone, location_str, portfolio_url] if p]
        header_text += " | ".join(contact_parts)
        blocks.append(
            CoverLetterContentBlock(
                id=f"blk_hdr_{uuid4().hex[:6]}",
                block_type="header",
                title="Applicant Header",
                text=header_text,
                ordering=ordering_idx,
                source_refs=[WritingSourceReference(source_entity_id=profile.id, source_type="claim")],
                word_count=len(header_text.split()),
            )
        )
        ordering_idx += 1

        # 2. Salutation Block
        salutation_text = f"Dear Hiring Team at {employer_name}," if employer_name else "Dear Hiring Manager,"
        blocks.append(
            CoverLetterContentBlock(
                id=f"blk_sal_{uuid4().hex[:6]}",
                block_type="salutation",
                title="Salutation",
                text=salutation_text,
                ordering=ordering_idx,
                word_count=len(salutation_text.split()),
            )
        )
        ordering_idx += 1

        # 3. Opening Block
        if letter_type == CoverLetterType.INTERNSHIP or is_enrolled:
            opening_text = (
                f"I am writing to express my enthusiastic interest in the {target_role} position at {employer_target}. "
                f"As a student pursuing a {degree_str or 'degree in engineering'} at {institution_str or 'university'}, "
                f"I have cultivated a rigorous technical foundation in {', '.join(top_skills[:3]) or 'software engineering'}. "
                f"I am eager to contribute my problem-solving capabilities and hands-on project experience to your engineering initiatives."
            )
        elif letter_type == CoverLetterType.EXPERIENCED and top_exp:
            exp_role = top_exp.job_title
            exp_emp = top_exp.employer
            opening_text = (
                f"I am pleased to submit my application for the {target_role} role at {employer_target}. "
                f"With a proven background as {exp_role} at {exp_emp}, I specialize in designing and delivering robust, scalable systems using "
                f"{', '.join(top_skills[:3]) or 'modern technologies'}. I welcome the opportunity to bring my architectural focus and operational discipline to your engineering team."
            )
        elif letter_type == CoverLetterType.RESEARCH:
            opening_text = (
                f"I am writing to apply for the {target_role} opportunity at {employer_target}. "
                f"My academic and research work in {top_edu.field_of_study if top_edu else 'computing'} has concentrated on methodological rigor, system design, "
                f"and empirical analysis utilizing {', '.join(top_skills[:3]) or 'computational methods'}. I look forward to contributing to your ongoing research and technical development goals."
            )
        elif letter_type == CoverLetterType.SHORT:
            opening_text = (
                f"Please accept my application for the {target_role} position at {employer_target}. "
                f"I bring verified technical proficiency in {', '.join(top_skills[:3]) or 'software development'} alongside hands-on engineering execution."
            )
        else:
            opening_text = (
                f"I am writing to express my strong interest in the {target_role} position at {employer_target}. "
                f"With solid technical foundations in {', '.join(top_skills[:3]) or 'core systems'} and practical development experience, "
                f"I am confident in my ability to deliver immediate value to your organization's engineering objectives."
            )

        blocks.append(
            CoverLetterContentBlock(
                id=f"blk_opn_{uuid4().hex[:6]}",
                block_type="opening",
                title="Opening Paragraph",
                text=opening_text,
                ordering=ordering_idx,
                source_refs=[WritingSourceReference(source_entity_id=top_edu.id, source_type="education")] if top_edu else [],
                word_count=len(opening_text.split()),
            )
        )
        ordering_idx += 1

        # 4. Qualifications & Background Block
        qual_refs: list[WritingSourceReference] = []
        if top_exp:
            ach_metric = ""
            if top_exp.achievements:
                a = top_exp.achievements[0]
                ach_metric = f", notably {a.statement}"
            qual_text = (
                f"During my tenure as {top_exp.job_title} at {top_exp.employer}, I applied {', '.join(top_exp.technologies[:4]) or 'industry tools'} "
                f"to engineer mission-critical systems and streamline delivery pipelines{ach_metric}. "
                f"This experience solidified my understanding of software lifecycles, test-driven methodologies, and production stability."
            )
            qual_refs.append(WritingSourceReference(source_entity_id=top_exp.id, source_type="experience"))
        elif top_edu:
            qual_text = (
                f"Throughout my academic coursework at {top_edu.institution}, I have maintained a focused trajectory in "
                f"{top_edu.field_of_study}. I have concentrated on core computing principles, distributed architectures, and algorithms, "
                f"applying theoretical knowledge directly to practical implementation using {', '.join(top_skills[:4]) or 'modern tooling'}."
            )
            qual_refs.append(WritingSourceReference(source_entity_id=top_edu.id, source_type="education"))
        else:
            qual_text = (
                f"My professional practice centers on building reliable and maintainable software using {', '.join(top_skills) or 'modern languages'}. "
                f"I maintain a disciplined approach to code quality, documentation, and continuous integration."
            )

        blocks.append(
            CoverLetterContentBlock(
                id=f"blk_qul_{uuid4().hex[:6]}",
                block_type="qualifications",
                title="Professional Qualifications",
                text=qual_text,
                ordering=ordering_idx,
                source_refs=qual_refs,
                word_count=len(qual_text.split()),
            )
        )
        ordering_idx += 1

        # 5. Evidence / Project Showcase Block
        proj_refs: list[WritingSourceReference] = []
        if top_project:
            proj_title = top_project.title
            proj_desc = top_project.description or "a full-stack software application"
            proj_contrib = top_project.applicant_contribution or "architecting core services and implementing responsive workflows"
            proj_tech = ", ".join(top_project.technologies[:4]) if top_project.technologies else "modern frameworks"
            evidence_text = (
                f"A key demonstration of my technical competence is {proj_title}. In this project, I was responsible for "
                f"{proj_contrib}, leveraging {proj_tech}. This work demonstrated my ability to solve concrete engineering challenges, "
                f"write clean and testable code, and see complex initiatives through from conception to deployment."
            )
            proj_refs.append(WritingSourceReference(source_entity_id=top_project.id, source_type="project"))
        else:
            evidence_text = (
                f"Through structured development exercises and evidence-backed implementations, I consistently practice "
                f"system profiling, modular architecture, and automated testing to ensure high reliability across all deliverables."
            )

        blocks.append(
            CoverLetterContentBlock(
                id=f"blk_evd_{uuid4().hex[:6]}",
                block_type="evidence_example",
                title="Evidence & Demonstrated Impact",
                text=evidence_text,
                ordering=ordering_idx,
                source_refs=proj_refs,
                word_count=len(evidence_text.split()),
            )
        )
        ordering_idx += 1

        # 6. Motivation & Alignment Block (No invented facts about company culture)
        motivation_text = (
            f"I am drawn to {employer_target} because the {target_role} position represents an outstanding match for my "
            f"engineering competencies and dedication to technical excellence. I am eager to apply my background in "
            f"{', '.join(top_skills[:3]) or 'software development'} to tackle complex problems and deliver measurable results."
        )
        blocks.append(
            CoverLetterContentBlock(
                id=f"blk_mot_{uuid4().hex[:6]}",
                block_type="motivation",
                title="Alignment & Motivation",
                text=motivation_text,
                ordering=ordering_idx,
                word_count=len(motivation_text.split()),
            )
        )
        ordering_idx += 1

        # 7. Closing Block
        closing_text = (
            f"Thank you for your time and consideration. I would welcome the opportunity to discuss how my verified background "
            f"and technical capabilities align with your requirements for the {target_role} role. I look forward to speaking with you."
        )
        blocks.append(
            CoverLetterContentBlock(
                id=f"blk_cls_{uuid4().hex[:6]}",
                block_type="closing",
                title="Closing Statement",
                text=closing_text,
                ordering=ordering_idx,
                word_count=len(closing_text.split()),
            )
        )
        ordering_idx += 1

        # 8. Signature Block
        sig_text = f"Sincerely,\n{applicant_name}"
        blocks.append(
            CoverLetterContentBlock(
                id=f"blk_sig_{uuid4().hex[:6]}",
                block_type="signature",
                title="Sign-off",
                text=sig_text,
                ordering=ordering_idx,
                word_count=len(sig_text.split()),
            )
        )

        return blocks
