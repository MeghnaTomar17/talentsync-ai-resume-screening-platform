skill_variations = {

    "python": ["python", "py"],

    "java": ["java"],

    "javascript": [
        "javascript",
        "js"
    ],

    "machine learning": [
        "machine learning",
        "ml"
    ],

    "sql": ["sql"],

    "html": ["html"],

    "css": ["css"],

    "git": [
        "git",
        "github"
    ],

    "communication": [
        "communication"
    ],

    "leadership": [
        "leadership"
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