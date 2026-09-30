"""
Regex-based Skill Extractor

Extracts skills from text using pattern matching and regular expressions.
Provides fast, rule-based extraction for common skill patterns.
"""

import re
from typing import List, Set, Tuple
from preprocessing.skill_normalizer import (
    SKILL_ALIASES,
    CANONICAL_SKILLS,
    LIST_ONLY_ALIASES,
    CASE_SENSITIVE_ALIASES,
    AMBIGUOUS_ALIASES,
)


# Common skill patterns
# These patterns help identify skills in various formats
SKILL_PATTERNS = [
    # Tech stack sections (e.g., "Skills: Python, Java, React")
    r'(?:skills|technologies|tech stack|stack|tools|languages|frameworks|libraries)[:\s]+([^.]+)',
    
    # Bullet points with skills
    r'(?:•|\-|\*|\d+\.)\s*([A-Z][a-zA-Z0-9+#\.\s]+?)(?:,|\n|$)',
    
    # Parenthetical skill mentions
    r'\(([^)]*?(?:python|java|react|angular|node|sql|aws|docker|kubernetes|git|api|rest|graphql)[^)]*)\)',
    
    # Skill with version numbers (e.g., "Python 3.8", "React 18")
    r'([A-Z][a-zA-Z0-9+#]+)\s*\d+(?:\.\d+)*',
    
    # Common technology combinations
    r'(?:MEAN|MERN|LAMP|PERN|JAMstack)',
    
    # Cloud service mentions
    r'(?:AWS|Azure|GCP|Google Cloud|EC2|S3|Lambda|Docker|Kubernetes|K8s)',
]


def _alias_pattern(alias: str) -> str:
    """
    Build a whole-word pattern for an alias.
    
    A plain word-boundary (\\b) pattern does not work for aliases that start
    or end with symbols: it never matches "C++", "C#" or ".NET". The
    lookarounds below treat letters, digits, '+', '#' (and a leading '.') as
    part of a token, so "c" does not match inside "c++" or "c#", and "js"
    does not match inside "node.js". Spaces in multi-word aliases also match
    hyphens and line breaks ("problem-solving", "time-\\nmanagement").
    """
    escaped = re.escape(alias).replace(r'\ ', r'[\s\-]+')
    return r'(?<![a-z0-9+#.])' + escaped + r'(?![a-z0-9+#])'


def _list_only_pattern(surface: str) -> str:
    """
    Pattern for an ambiguous alias that is only accepted inside a list,
    e.g. "Languages: C, C++, R" or "C/C++". Matched case-sensitively.
    """
    before = r'(?:^|[,:;|/(\u2022])[ \t]*'
    after = r'[ \t]*(?=[,;|/).]|$)'
    return before + re.escape(surface) + after


def extract_skills_with_regex(text: str) -> List[str]:
    """
    Extract skills from text using regex pattern matching.
    
    Args:
        text: Input text (cleaned resume or job description)
        
    Returns:
        List of extracted skill strings (not yet normalized)
    """
    extracted = set()
    text_lower = text.lower()
    
    # Method 1: Direct keyword matching from our alias list
    # (aliases and canonical names, matched as whole tokens)
    vocabulary = {**SKILL_ALIASES, **CANONICAL_SKILLS}
    for alias, canonical in vocabulary.items():
        if alias in AMBIGUOUS_ALIASES:
            continue
        if re.search(_alias_pattern(alias.lower()), text_lower):
            extracted.add(canonical)
    
    # Method 1b: Ambiguous aliases, accepted only in their technology form
    for alias, surface in LIST_ONLY_ALIASES.items():
        if re.search(_list_only_pattern(surface), text, re.MULTILINE):
            extracted.add(SKILL_ALIASES[alias])
    
    for alias, surface in CASE_SENSITIVE_ALIASES.items():
        if re.search(r'(?<![A-Za-z0-9+#.])' + re.escape(surface) + r'(?![A-Za-z0-9+#])', text):
            extracted.add(SKILL_ALIASES[alias])
    
    # Method 2: Pattern-based extraction
    for pattern in SKILL_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            # Clean and split the match
            cleaned = match.strip()
            # Split by common separators
            skills = re.split(r'[,;|/]', cleaned)
            for skill in skills:
                skill = skill.strip()
                # Filter out very short matches and ambiguous words
                # (those are handled by Method 1b above)
                if len(skill) > 2 and skill.lower() not in AMBIGUOUS_ALIASES:
                    extracted.add(skill)
    
    # Method 3: Look for capitalized words in skill-like contexts
    # Find sequences of capitalized words (likely proper nouns/technologies)
    cap_pattern = r'\b([A-Z][a-zA-Z0-9+#]*\.?[a-zA-Z0-9+#]*)\b'
    cap_matches = re.findall(cap_pattern, text)
    
    # Filter capitalized words that are likely skills
    common_words = {'The', 'This', 'That', 'These', 'Those', 'And', 'Or', 'But',
                    'With', 'From', 'To', 'For', 'In', 'On', 'At', 'By', 'Of',
                    'As', 'Is', 'Are', 'Was', 'Were', 'Be', 'Been', 'Being',
                    'Have', 'Has', 'Had', 'Do', 'Does', 'Did', 'Will', 'Would',
                    'Could', 'Should', 'May', 'Might', 'Must', 'Can', 'Need',
                    'Project', 'Experience', 'Education', 'Work', 'Job', 'Role',
                    'Company', 'Team', 'Manager', 'Developer', 'Engineer',
                    'January', 'February', 'March', 'April', 'May', 'June',
                    'July', 'August', 'September', 'October', 'November', 'December'}
    
    for match in cap_matches:
        if (match not in common_words and len(match) > 2
                and match.lower() not in AMBIGUOUS_ALIASES):
            # Check if it looks like a technology (contains numbers, dots, etc.)
            if re.search(r'[0-9+#\.]', match) or match[0].isupper():
                extracted.add(match)
    
    return list(extracted)


def extract_skills_with_confidence(text: str) -> List[Tuple[str, float]]:
    """
    Extract skills with confidence scores based on extraction method.
    
    Args:
        text: Input text
        
    Returns:
        List of (skill, confidence) tuples
    """
    skills = extract_skills_with_regex(text)
    
    # Assign confidence based on how the skill was found
    results = []
    for skill in skills:
        # Direct alias match gets higher confidence
        skill_lower = skill.lower()
        if skill_lower in SKILL_ALIASES:
            results.append((skill, 0.9))
        elif any(alias.lower() in skill_lower for alias in SKILL_ALIASES.keys()):
            results.append((skill, 0.7))
        else:
            results.append((skill, 0.5))
    
    return results
