"""
Skill Gap Analysis

Compares resume skills with job skills and sorts every job skill into:

- matched: the skill was detected in the resume
- partial: the skill was not detected, but a closely related skill was
           (e.g. job asks for PostgreSQL, resume has MySQL)
- missing: every job skill that was not matched (partial ones included,
           so existing consumers of "missing skills" keep the same meaning)

Related skills come from a small, controlled list of groups using the
canonical names from preprocessing/skill_normalizer.py. Partial matches are
reported for explainability only; they do not change the ATS score.
"""

from typing import Dict, List, Any


# Skills in the same group can partly substitute for each other.
RELATED_SKILL_GROUPS = [
    {"SQL", "PostgreSQL", "MySQL", "SQLite", "MariaDB", "Microsoft SQL Server", "Oracle Database"},
    {"MongoDB", "Cassandra", "DynamoDB", "Firebase"},
    {"AWS", "Microsoft Azure", "Google Cloud Platform", "IBM Cloud", "Oracle Cloud", "Alibaba Cloud"},
    {"Docker", "Kubernetes", "Helm"},
    {"CI/CD", "Jenkins", "GitHub Actions", "GitLab", "CircleCI", "Travis CI", "ArgoCD"},
    {"Terraform", "Ansible", "Pulumi", "Chef", "Puppet"},
    {"Django", "Flask", "FastAPI"},
    {"Node.js", "Express.js", "NestJS"},
    {"React", "Angular", "AngularJS", "Vue.js", "Svelte", "Next.js"},
    {"JavaScript", "TypeScript"},
    {".NET", "ASP.NET", "C#"},
    {"Java", "Spring Boot"},
    {"TensorFlow", "PyTorch", "Keras"},
    {"Machine Learning", "Deep Learning"},
    {"scikit-learn", "XGBoost", "LightGBM", "CatBoost"},
    {"Tableau", "Power BI", "QlikView"},
    {"Apache Spark", "PySpark", "Hadoop", "Databricks"},
    {"Snowflake", "BigQuery", "Redshift", "Data Warehousing"},
    {"Git", "GitHub", "GitLab", "Bitbucket"},
    {"Jest", "Mocha", "Cypress", "Selenium", "Playwright", "PyTest", "JUnit"},
    {"React Native", "Flutter", "Xamarin", "Ionic"},
    {"Apache Kafka", "RabbitMQ", "ActiveMQ"},
    {"Prometheus", "Grafana", "Datadog", "New Relic", "Splunk", "ELK Stack"},
    {"Agile Methodology", "Scrum", "Kanban"},
    {"CSS", "Bootstrap", "Tailwind CSS"},
    {"Linux", "Unix", "Shell Scripting"},
]


def get_related_skills(skill: str) -> set:
    """
    Get the skills related to a canonical skill (excluding the skill itself).
    
    Args:
        skill: Canonical skill name
        
    Returns:
        Set of related canonical skill names
    """
    related = set()
    for group in RELATED_SKILL_GROUPS:
        if skill in group:
            related |= group
    related.discard(skill)
    return related


def analyze_skill_gaps(resume_skills: List[str], job_skills: List[str]) -> Dict[str, Any]:
    """
    Categorize job skills into matched, partial and missing.
    
    Args:
        resume_skills: Canonical skills detected in the resume
        job_skills: Canonical skills detected in the job description
        
    Returns:
        Dictionary containing:
        - matched_skills: sorted list of job skills found in the resume
        - missing_skills: sorted list of job skills not found in the resume
        - partial_matches: list of {"skill", "related_skills"} for missing
          skills where the resume has a related skill
    """
    resume_set = set(resume_skills)
    job_set = set(job_skills)
    
    matched = sorted(job_set & resume_set)
    missing = sorted(job_set - resume_set)
    
    partial_matches = []
    for skill in missing:
        related_in_resume = sorted(get_related_skills(skill) & resume_set)
        if related_in_resume:
            partial_matches.append({
                "skill": skill,
                "related_skills": related_in_resume
            })
    
    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "partial_matches": partial_matches
    }
