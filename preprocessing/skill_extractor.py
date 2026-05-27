skill_variations = {

    "python": ["python", "py"],

    "java": ["java"],

    "javascript": ["javascript", "js"],

    "typescript": ["typescript", "ts"],

    "react": ["react", "reactjs"],

    "nodejs": ["node", "nodejs"],

    "machine learning": [
        "machine learning",
        "ml"
    ],

    "deep learning": [
        "deep learning"
    ],

    "nlp": [
        "nlp",
        "natural language processing"
    ],

    "sql": ["sql"],

    "mongodb": ["mongodb"],

    "mysql": ["mysql"],

    "html": ["html"],

    "css": ["css"],

    "git": [
        "git",
        "github"
    ],

    "docker": ["docker"],

    "aws": ["aws"],

    "tensorflow": ["tensorflow"],

    "pytorch": ["pytorch"],

    "data analysis": [
        "data analysis",
        "analytics"
    ],

    "communication": [
        "communication"
    ],

    "leadership": [
        "leadership"
    ],

    "problem solving": [
        "problem solving"
    ],

    "teamwork": [
        "teamwork"
    ]
}


def advanced_skill_extractor(text):

    extracted_skills = set()

    tokens = text.split()

    clean_text = " ".join(tokens)

    for standard_skill, variations in skill_variations.items():

        for variation in variations:

            variation = variation.lower()

            if " " in variation:

                if variation in clean_text:
                    extracted_skills.add(
                        standard_skill
                    )

            else:

                if variation in tokens:
                    extracted_skills.add(
                        standard_skill
                    )

    return list(extracted_skills)