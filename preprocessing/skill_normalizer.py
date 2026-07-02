"""
Skill Normalization Module

Handles skill alias mapping and canonical normalization.
Converts various skill representations to standard canonical names.
"""

from typing import Dict, List, Tuple


# Comprehensive skill alias mapping
# Maps aliases and variations to canonical skill names
SKILL_ALIASES = {
    # Programming Languages
    "js": "JavaScript",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "python": "Python",
    "py": "Python",
    "java": "Java",
    "c++": "C++",
    "cpp": "C++",
    "c#": "C#",
    "csharp": "C#",
    "c": "C",
    "go": "Go",
    "golang": "Go",
    "rust": "Rust",
    "ruby": "Ruby",
    "php": "PHP",
    "swift": "Swift",
    "kotlin": "Kotlin",
    "scala": "Scala",
    "r": "R",
    "matlab": "MATLAB",
    "perl": "Perl",
    "lua": "Lua",
    "dart": "Dart",
    "julia": "Julia",
    "haskell": "Haskell",
    "elixir": "Elixir",
    "erlang": "Erlang",
    "clojure": "Clojure",
    "f#": "F#",
    "fsharp": "F#",
    "groovy": "Groovy",
    "shell": "Shell Scripting",
    "bash": "Shell Scripting",
    "powershell": "PowerShell",
    "sql": "SQL",
    
    # Frontend Frameworks
    "react": "React",
    "reactjs": "React",
    "react.js": "React",
    "react native": "React Native",
    "reactnative": "React Native",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "vue.js": "Vue.js",
    "angular": "Angular",
    "angularjs": "AngularJS",
    "angular.js": "AngularJS",
    "svelte": "Svelte",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "nuxt": "Nuxt.js",
    "nuxtjs": "Nuxt.js",
    "gatsby": "Gatsby",
    "ember": "Ember.js",
    "emberjs": "Ember.js",
    "backbone": "Backbone.js",
    "backbonejs": "Backbone.js",
    "jquery": "jQuery",
    
    # Backend Frameworks
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "express": "Express.js",
    "expressjs": "Express.js",
    "express.js": "Express.js",
    "django": "Django",
    "flask": "Flask",
    "fastapi": "FastAPI",
    "spring": "Spring Boot",
    "spring boot": "Spring Boot",
    "springboot": "Spring Boot",
    "rails": "Ruby on Rails",
    "ruby on rails": "Ruby on Rails",
    "laravel": "Laravel",
    "asp.net": "ASP.NET",
    "aspnet": "ASP.NET",
    "nest": "NestJS",
    "nestjs": "NestJS",
    "koa": "Koa.js",
    "hapi": "Hapi.js",
    "falcon": "Falcon",
    "tornado": "Tornado",
    "sanic": "Sanic",
    "aiohttp": "aiohttp",
    
    # Databases
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "sqlite": "SQLite",
    "redis": "Redis",
    "elasticsearch": "Elasticsearch",
    "elasticsearch": "Elasticsearch",
    "cassandra": "Cassandra",
    "dynamodb": "DynamoDB",
    "neo4j": "Neo4j",
    "influxdb": "InfluxDB",
    "firebase": "Firebase",
    "supabase": "Supabase",
    "cockroachdb": "CockroachDB",
    "mariadb": "MariaDB",
    "oracle": "Oracle Database",
    "mssql": "Microsoft SQL Server",
    "sql server": "Microsoft SQL Server",
    
    # Cloud Platforms
    "aws": "AWS",
    "amazon web services": "AWS",
    "azure": "Microsoft Azure",
    "gcp": "Google Cloud Platform",
    "google cloud": "Google Cloud Platform",
    "ibm cloud": "IBM Cloud",
    "heroku": "Heroku",
    "digitalocean": "DigitalOcean",
    "linode": "Linode",
    "vercel": "Vercel",
    "netlify": "Netlify",
    "alibaba cloud": "Alibaba Cloud",
    "oracle cloud": "Oracle Cloud",
    
    # AI/ML
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "deep learning": "Deep Learning",
    "nlp": "Natural Language Processing",
    "natural language processing": "Natural Language Processing",
    "computer vision": "Computer Vision",
    "tensorflow": "TensorFlow",
    "tf": "TensorFlow",
    "pytorch": "PyTorch",
    "keras": "Keras",
    "scikit-learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "scipy": "SciPy",
    "matplotlib": "Matplotlib",
    "seaborn": "Seaborn",
    "opencv": "OpenCV",
    "hugging face": "Hugging Face",
    "transformers": "Hugging Face Transformers",
    "langchain": "LangChain",
    "openai": "OpenAI",
    "anthropic": "Anthropic",
    "stable diffusion": "Stable Diffusion",
    "llm": "Large Language Models",
    "large language models": "Large Language Models",
    "generative ai": "Generative AI",
    "reinforcement learning": "Reinforcement Learning",
    "xgboost": "XGBoost",
    "lightgbm": "LightGBM",
    "catboost": "CatBoost",
    "spark": "Apache Spark",
    "pyspark": "PySpark",
    "mlflow": "MLflow",
    "wandb": "Weights & Biases",
    "comet": "Comet ML",
    
    # DevOps
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "jenkins": "Jenkins",
    "gitlab": "GitLab",
    "github actions": "GitHub Actions",
    "circleci": "CircleCI",
    "travisci": "Travis CI",
    "ansible": "Ansible",
    "terraform": "Terraform",
    "pulumi": "Pulumi",
    "chef": "Chef",
    "puppet": "Puppet",
    "helm": "Helm",
    "argocd": "ArgoCD",
    "prometheus": "Prometheus",
    "grafana": "Grafana",
    "elk": "ELK Stack",
    "logstash": "Logstash",
    "kibana": "Kibana",
    "nagios": "Nagios",
    "datadog": "Datadog",
    "new relic": "New Relic",
    "splunk": "Splunk",
    
    # Tools & Libraries
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",
    "bitbucket": "Bitbucket",
    "svn": "Subversion",
    "mercurial": "Mercurial",
    "jira": "Jira",
    "confluence": "Confluence",
    "slack": "Slack",
    "trello": "Trello",
    "asana": "Asana",
    "notion": "Notion",
    "figma": "Figma",
    "sketch": "Sketch",
    "adobe xd": "Adobe XD",
    "postman": "Postman",
    "swagger": "Swagger",
    "openapi": "OpenAPI",
    "graphql": "GraphQL",
    "rest": "REST API",
    "restful": "REST API",
    "soap": "SOAP",
    "grpc": "gRPC",
    "websocket": "WebSocket",
    "kafka": "Apache Kafka",
    "rabbitmq": "RabbitMQ",
    "activemq": "ActiveMQ",
    "nginx": "Nginx",
    "apache": "Apache HTTP Server",
    
    # Soft Skills
    "communication": "Communication",
    "leadership": "Leadership",
    "teamwork": "Teamwork",
    "problem solving": "Problem Solving",
    "critical thinking": "Critical Thinking",
    "time management": "Time Management",
    "project management": "Project Management",
    "agile": "Agile Methodology",
    "scrum": "Scrum",
    "kanban": "Kanban",
    "collaboration": "Collaboration",
    "adaptability": "Adaptability",
    "creativity": "Creativity",
    "innovation": "Innovation",
    "analytical thinking": "Analytical Thinking",
    "decision making": "Decision Making",
    "mentoring": "Mentoring",
    "presentation": "Presentation Skills",
    "negotiation": "Negotiation",
    "conflict resolution": "Conflict Resolution",
}


def normalize_skill(skill: str) -> Tuple[str, float]:
    """
    Normalize a skill to its canonical form.
    
    Args:
        skill: Raw skill string
        
    Returns:
        Tuple of (canonical_skill, confidence_score)
        confidence_score: 1.0 for exact match, 0.8 for alias match
    """
    skill_lower = skill.lower().strip()
    
    # Check for exact match (case-insensitive)
    for canonical, aliases in SKILL_ALIASES.items():
        if canonical.lower() == skill_lower:
            return (canonical, 1.0)
    
    # Check for alias match
    if skill_lower in SKILL_ALIASES:
        return (SKILL_ALIASES[skill_lower], 0.8)
    
    # Check if skill contains a known alias (substring match)
    for alias, canonical in SKILL_ALIASES.items():
        if alias.lower() in skill_lower or skill_lower in alias.lower():
            return (canonical, 0.6)
    
    # Return original if no match found
    return (skill, 0.5)


def normalize_skills(skills: List[str]) -> List[Tuple[str, float]]:
    """
    Normalize a list of skills to canonical forms.
    
    Args:
        skills: List of raw skill strings
        
    Returns:
        List of tuples (canonical_skill, confidence_score)
    """
    normalized = []
    seen = set()
    
    for skill in skills:
        canonical, confidence = normalize_skill(skill)
        
        # Remove duplicates while preserving highest confidence
        if canonical not in seen:
            normalized.append((canonical, confidence))
            seen.add(canonical)
        else:
            # Update confidence if this match has higher confidence
            for i, (existing_skill, existing_conf) in enumerate(normalized):
                if existing_skill == canonical and confidence > existing_conf:
                    normalized[i] = (canonical, confidence)
                    break
    
    return normalized
