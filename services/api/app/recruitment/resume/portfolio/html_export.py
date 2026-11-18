"""Static Standalone HTML Portfolio Export Engine (Stage 23)."""

from __future__ import annotations

import logging
from pathlib import Path
from app.recruitment.resume.contracts import PortfolioDocument
from app.recruitment.resume.errors import DocumentExportError

logger = logging.getLogger("autonom.recruitment.resume.portfolio.html_export")


class PortfolioHtmlRenderer:
    """Generates standalone, locally viewable HTML portfolio packages."""

    @classmethod
    def render_to_file(
        cls,
        portfolio: PortfolioDocument,
        output_path: str,
    ) -> str:
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            skills_html = ""
            if portfolio.selected_skills:
                pills = "".join(f'<span class="skill-pill">{s}</span>' for s in portfolio.selected_skills)
                skills_html = f'<div class="skills-bar"><h3>Technical Expertise</h3><div class="pills-wrap">{pills}</div></div>'

            projects_html = []
            for prj in portfolio.selected_projects:
                tech_badges = "".join(f'<span class="tech-badge">{t}</span>' for t in prj.tech_stack)
                deliv_items = "".join(f'<li>{d}</li>' for d in prj.deliverables)

                repo_link = ""
                if prj.repo_url and prj.is_public_eligible:
                    repo_link = f'<a href="{prj.repo_url}" class="repo-link" target="_blank" rel="noopener">View Source &rarr;</a>'

                card = f"""
                <div class="project-card">
                    <div class="project-card-header">
                        <h4>{prj.title}</h4>
                        {repo_link}
                    </div>
                    <div class="tech-row">{tech_badges}</div>
                    <p class="summary">{prj.summary}</p>
                    {f'<p class="problem"><strong>Challenge:</strong> {prj.problem_addressed}</p>' if prj.problem_addressed else ''}
                    <p class="contribution"><strong>My Contribution:</strong> {prj.individual_contribution}</p>
                    {f'<ul class="deliverables">{deliv_items}</ul>' if deliv_items else ''}
                </div>
                """
                projects_html.append(card)

            html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{portfolio.title}</title>
    <style>
        :root {{
            --bg-color: #0F172A;
            --surface-color: #1E293B;
            --text-main: #F8FAFC;
            --text-muted: #94A3B8;
            --accent: #38BDF8;
            --accent-hover: #0EA5E9;
            --border: #334155;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            line-height: 1.6;
            padding: 2rem 1rem;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        header {{
            text-align: center;
            padding-bottom: 2rem;
            border-bottom: 1px solid var(--border);
            margin-bottom: 2rem;
        }}
        h1 {{ font-size: 2.25rem; color: #FFFFFF; margin-bottom: 0.5rem; }}
        .intro {{ font-size: 1.1rem; color: var(--text-muted); max-width: 700px; margin: 0 auto; }}
        .skills-bar {{
            background: var(--surface-color);
            padding: 1.5rem;
            border-radius: 8px;
            border: 1px solid var(--border);
            margin-bottom: 2.5rem;
        }}
        .skills-bar h3 {{ font-size: 1.1rem; margin-bottom: 1rem; color: var(--accent); }}
        .pills-wrap {{ display: flex; flex-wrap: wrap; gap: 0.5rem; }}
        .skill-pill {{
            background: rgba(56, 189, 248, 0.15);
            color: var(--accent);
            padding: 0.35rem 0.75rem;
            border-radius: 4px;
            font-size: 0.875rem;
            font-weight: 500;
        }}
        .projects-section h2 {{
            font-size: 1.5rem;
            margin-bottom: 1.5rem;
            border-left: 4px solid var(--accent);
            padding-left: 0.75rem;
        }}
        .project-card {{
            background: var(--surface-color);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }}
        .project-card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.75rem;
        }}
        .project-card-header h4 {{ font-size: 1.25rem; color: #FFFFFF; }}
        .repo-link {{
            color: var(--accent);
            text-decoration: none;
            font-size: 0.875rem;
            font-weight: 600;
        }}
        .repo-link:hover {{ text-decoration: underline; }}
        .tech-row {{ display: flex; flex-wrap: wrap; gap: 0.4rem; margin-bottom: 1rem; }}
        .tech-badge {{
            background: #0F172A;
            border: 1px solid var(--border);
            color: var(--text-muted);
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
        }}
        .summary {{ margin-bottom: 0.75rem; }}
        .problem, .contribution {{ font-size: 0.95rem; margin-bottom: 0.5rem; }}
        .deliverables {{
            margin-top: 0.75rem;
            padding-left: 1.25rem;
            color: var(--text-muted);
            font-size: 0.9rem;
        }}
        footer {{
            text-align: center;
            margin-top: 3rem;
            padding-top: 1.5rem;
            border-top: 1px solid var(--border);
            color: var(--text-muted);
            font-size: 0.85rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{portfolio.title}</h1>
            <p class="intro">{portfolio.professional_intro}</p>
        </header>
        {skills_html}
        <section class="projects-section">
            <h2>Featured Engineering Work</h2>
            {"".join(projects_html)}
        </section>
        <footer>
            <p>Generated by AUTONOM Technical Portfolio Intelligence</p>
        </footer>
    </div>
</body>
</html>
"""
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html)

            logger.info(f"Rendered Portfolio HTML successfully to '{output_path}'.")
            return output_path

        except Exception as exc:
            logger.error(f"Error rendering Portfolio HTML to '{output_path}': {exc}")
            raise DocumentExportError(f"Portfolio HTML rendering failed: {exc}") from exc
