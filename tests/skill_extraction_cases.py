"""
Labelled resumes used to evaluate skill extraction.

Each case lists the skills a human reviewer expects (canonical names from
preprocessing/skill_normalizer.py) and an optional "acceptable" set: skills
that are defensible either way and are counted neither as misses nor as
false positives.

The synthetic resumes contain deliberate traps (name initials, company names
and ordinary English words that are also technology names) so that recall
improvements cannot be bought with uncontrolled false positives.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


SYNTHETIC_CASES = [
    {
        "name": "synthetic_python_backend",
        "text": """Rahul Mehta
Pune, Maharashtra | rahul.mehta@example.com

SUMMARY
Backend developer with 2 years of experience building REST APIs.

TECHNICAL SKILLS
Languages: Python, C++, SQL
Frameworks: FastAPI, Django, Flask
Databases: Postgres, MongoDB, Redis
Tools: Git, Docker, Linux

EXPERIENCE
Software Engineer Intern - Acme Corp, Rest Ave, Bengaluru
- Built a RESTful service using FastAPI and PostgreSQL deployed on AWS EC2.
- Containerised services with Docker and set up CI/CD pipelines with GitHub Actions.

PROJECTS
Resume Ranker - Implemented semantic search with scikit learn and NumPy.
""",
        "expected": {
            "Python", "C++", "SQL", "FastAPI", "Django", "Flask", "PostgreSQL",
            "MongoDB", "Redis", "Git", "Docker", "Linux", "REST API", "AWS",
            "CI/CD", "GitHub Actions", "scikit-learn", "NumPy",
        },
        "acceptable": {"GitHub"},
    },
    {
        "name": "synthetic_dotnet_fullstack",
        "text": """Priya R
Chennai

Full stack developer skilled in C#, ASP.NET Core, .NET 6, ReactJS, Node.js,
TypeScript, HTML5 and CSS3.

EXPERIENCE
Developer, Go Digital Solutions (2021 - Present)
- Developed Web API services in C# backed by SQL Server.
- Built single page apps with React.js and wrote unit tests with Jest.

SKILLS
C#, .NET, ASP.NET, React, Node.js, TypeScript, JavaScript, HTML, CSS,
Microsoft SQL Server, Jest, Agile, Scrum
""",
        "expected": {
            "C#", ".NET", "ASP.NET", "React", "Node.js", "TypeScript",
            "JavaScript", "HTML", "CSS", "Microsoft SQL Server", "Jest",
            "Agile Methodology", "Scrum", "Web API",
        },
        "acceptable": {"SQL"},
    },
    {
        "name": "synthetic_data_scientist",
        "text": """Aman Verma | Delhi
Data Scientist

Skills
Machine Learning, Deep Learning, NLP, sklearn, TensorFlow, PyTorch, Pandas,
NumPy, Matplotlib, Tableau, Power BI, Excel

Experience
Analyst, Spring Valley Foods
- Built churn prediction models using XGBoost and scikit-learn on Spark.
- Presented dashboards in Power BI to leadership; strong communication skills.

Education: B.Tech, Computer Science
""",
        "expected": {
            "Machine Learning", "Deep Learning", "Natural Language Processing",
            "scikit-learn", "TensorFlow", "PyTorch", "Pandas", "NumPy",
            "Matplotlib", "Tableau", "Power BI", "Microsoft Excel", "XGBoost",
            "Apache Spark", "Communication",
        },
        "acceptable": {"Leadership"},
    },
    {
        "name": "synthetic_non_technical_traps",
        "text": """Neha Kapoor
Sales Executive

Summary: Energetic sales professional. Ready to go the extra mile and
enjoys rest days spent travelling.

Experience
Sales Executive, Oracle Towers Realty
Account Manager, Swift Logistics
- Managed client relationships and negotiation with vendors.
- Prepared weekly reports in MS Excel.

Skills: Negotiation, Communication, Time Management, MS Excel
""",
        "expected": {
            "Negotiation", "Communication", "Time Management", "Microsoft Excel",
        },
        "acceptable": set(),
    },
]


PDF_CASES = [
    {
        # Dataset resume shipped with the repo (INFORMATION-TECHNOLOGY category).
        "name": "sample_resume/sample.pdf",
        "pdf": ROOT / "sample_resume" / "sample.pdf",
        "expected": {
            "SQL", "Scrum", "VMware", "Active Directory", "PowerShell",
            "Windows", "Microsoft Exchange", "Microsoft Office", "Communication",
        },
        "acceptable": {"Project Management"},
    },
    {
        # Local-only: temp_resume.pdf is git-ignored because it is a real
        # candidate's resume. The case is skipped when the file is absent.
        "name": "temp_resume.pdf (local only)",
        "pdf": ROOT / "temp_resume.pdf",
        "expected": {
            ".NET", "ASP.NET", "C#", "AngularJS", "HTML", "CSS", "JavaScript",
            "SQL", "Web API", "REST API", "QlikView", "Communication",
            "Time Management", "Problem Solving",
        },
        "acceptable": {"Innovation"},
    },
]
