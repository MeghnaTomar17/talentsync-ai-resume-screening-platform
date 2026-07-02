"""
Skill Categorization Module

Categorizes skills into predefined categories for better organization and analysis.
"""

from typing import Dict, List, Set


# Skill categories with their associated skills
SKILL_CATEGORIES = {
    "Programming Languages": {
        "JavaScript", "TypeScript", "Python", "Java", "C++", "C#", "C", "Go",
        "Rust", "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "MATLAB",
        "Perl", "Lua", "Dart", "Julia", "Haskell", "Elixir", "Erlang",
        "Clojure", "F#", "Groovy", "Shell Scripting", "PowerShell", "SQL"
    },
    
    "Frontend Frameworks": {
        "React", "React Native", "Vue.js", "Angular", "AngularJS", "Svelte",
        "Next.js", "Nuxt.js", "Gatsby", "Ember.js", "Backbone.js", "jQuery"
    },
    
    "Backend Frameworks": {
        "Node.js", "Express.js", "Django", "Flask", "FastAPI", "Spring Boot",
        "Ruby on Rails", "Laravel", "ASP.NET", "NestJS", "Koa.js", "Hapi.js",
        "Falcon", "Tornado", "Sanic", "aiohttp"
    },
    
    "Databases": {
        "MongoDB", "MySQL", "PostgreSQL", "SQLite", "Redis", "Elasticsearch",
        "Cassandra", "DynamoDB", "Neo4j", "InfluxDB", "Firebase", "Supabase",
        "CockroachDB", "MariaDB", "Oracle Database", "Microsoft SQL Server"
    },
    
    "Cloud Platforms": {
        "AWS", "Microsoft Azure", "Google Cloud Platform", "IBM Cloud",
        "Heroku", "DigitalOcean", "Linode", "Vercel", "Netlify",
        "Alibaba Cloud", "Oracle Cloud"
    },
    
    "AI/ML": {
        "Machine Learning", "Deep Learning", "Natural Language Processing",
        "Computer Vision", "TensorFlow", "PyTorch", "Keras", "scikit-learn",
        "Pandas", "NumPy", "SciPy", "Matplotlib", "Seaborn", "OpenCV",
        "Hugging Face Transformers", "LangChain", "OpenAI", "Anthropic",
        "Stable Diffusion", "Large Language Models", "Generative AI",
        "Reinforcement Learning", "XGBoost", "LightGBM", "CatBoost",
        "Apache Spark", "PySpark", "MLflow", "Weights & Biases", "Comet ML"
    },
    
    "DevOps": {
        "Docker", "Kubernetes", "Jenkins", "GitLab", "GitHub Actions",
        "CircleCI", "Travis CI", "Ansible", "Terraform", "Pulumi", "Chef",
        "Puppet", "Helm", "ArgoCD", "Prometheus", "Grafana", "ELK Stack",
        "Logstash", "Kibana", "Nagios", "Datadog", "New Relic", "Splunk"
    },
    
    "Tools & Libraries": {
        "Git", "GitHub", "GitLab", "Bitbucket", "Subversion", "Mercurial",
        "Jira", "Confluence", "Slack", "Trello", "Asana", "Notion", "Figma",
        "Sketch", "Adobe XD", "Postman", "Swagger", "OpenAPI", "GraphQL",
        "REST API", "SOAP", "gRPC", "WebSocket", "Apache Kafka", "RabbitMQ",
        "ActiveMQ", "Nginx", "Apache HTTP Server"
    },
    
    "Soft Skills": {
        "Communication", "Leadership", "Teamwork", "Problem Solving",
        "Critical Thinking", "Time Management", "Project Management",
        "Agile Methodology", "Scrum", "Kanban", "Collaboration",
        "Adaptability", "Creativity", "Innovation", "Analytical Thinking",
        "Decision Making", "Mentoring", "Presentation Skills", "Negotiation",
        "Conflict Resolution"
    },
    
    "Data Engineering": {
        "Apache Spark", "PySpark", "Apache Kafka", "Apache Flink",
        "Apache Airflow", "dbt", "Snowflake", "Databricks", "BigQuery",
        "Redshift", "Data Warehousing", "ETL", "Data Pipelines"
    },
    
    "Mobile Development": {
        "React Native", "Flutter", "Swift", "Kotlin", "iOS", "Android",
        "Xamarin", "Ionic", "Cordova"
    },
    
    "Testing": {
        "Jest", "Mocha", "Chai", "Selenium", "Cypress", "Playwright",
        "PyTest", "JUnit", "TestNG", "RSpec", "PHPUnit"
    },
    
    "Security": {
        "OAuth", "JWT", "SSL/TLS", "Penetration Testing", "OWASP",
        "Cybersecurity", "Network Security", "Application Security"
    }
}


def categorize_skill(skill: str) -> str:
    """
    Categorize a single skill into its appropriate category.
    
    Args:
        skill: Canonical skill name
        
    Returns:
        Category name or "Uncategorized" if not found
    """
    for category, skills in SKILL_CATEGORIES.items():
        if skill in skills:
            return category
    
    return "Uncategorized"


def categorize_skills(skills: List[str]) -> Dict[str, List[str]]:
    """
    Categorize a list of skills into their respective categories.
    
    Args:
        skills: List of canonical skill names
        
    Returns:
        Dictionary mapping category names to lists of skills
    """
    categorized = {category: [] for category in SKILL_CATEGORIES.keys()}
    categorized["Uncategorized"] = []
    
    for skill in skills:
        category = categorize_skill(skill)
        if category in categorized:
            categorized[category].append(skill)
    
    # Remove empty categories
    return {k: v for k, v in categorized.items() if v}


def get_category_skills(category: str) -> Set[str]:
    """
    Get all skills in a specific category.
    
    Args:
        category: Category name
        
    Returns:
        Set of skills in the category
    """
    return SKILL_CATEGORIES.get(category, set())


def get_all_categories() -> List[str]:
    """
    Get all available category names.
    
    Returns:
        List of category names
    """
    return list(SKILL_CATEGORIES.keys())
