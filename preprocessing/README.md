# Production-Ready Skill Extraction Pipeline

## Overview

This module provides a production-ready, multi-method skill extraction pipeline that primarily uses regex-based pattern matching with normalization and categorization. LLM-powered extraction is available as an optional enhancement for improved accuracy when needed.

## Architecture

### Components

- **`skill_normalizer.py`**: Skill alias mapping and canonical normalization
  - Maps 200+ skill aliases to canonical names
  - Handles variations like "JS" → "JavaScript", "ReactJS" → "React"
  - Provides confidence scores for matches

- **`skill_categorizer.py`**: Skill categorization by domain
  - 14 predefined categories (Languages, Frameworks, Databases, Cloud, AI/ML, etc.)
  - Automatic category assignment
  - Extensible category system

- **`regex_skill_extractor.py`**: Fast pattern-based extraction
  - Multiple regex patterns for skill detection
  - Capitalized word recognition
  - Tech stack section parsing
  - Version number handling

- **`llm_skill_extractor.py`**: Intelligent LLM-based extraction
  - Uses Google Gemini for context-aware extraction
  - Can identify skills in natural language context
  - Optional detailed categorization via LLM

- **`skill_extraction_pipeline.py`**: Main orchestration logic
  - Combines regex and LLM extraction methods
  - Merges and deduplicates results
  - Normalizes and categorizes skills
  - Returns structured output with metadata

- **`skill_extractor.py`**: Public interface (backward-compatible)
  - Maintains compatibility with existing code
  - Simple list-based output for legacy integration

## Extraction Strategy

### Primary Method: Regex-Based Extraction (Default)

1. **Regex Extraction** (Fast, ~10ms)
   - Pattern matching for common skill formats
   - Direct keyword matching from alias list
   - Tech stack section parsing
   - Capitalized word recognition

2. **Normalization**
   - Alias mapping to canonical names
   - Duplicate removal
   - Confidence score calculation

3. **Categorization**
   - Rule-based category assignment
   - 14 predefined categories

### Optional Enhancement: LLM-Based Extraction

4. **LLM Extraction** (Intelligent, ~2-5s) - Optional
   - Context-aware skill identification
   - Natural language understanding
   - Can catch skills missed by patterns
   - Optional categorization via LLM
   
   **Note:** LLM extraction is disabled by default. Enable explicitly for enhanced accuracy.

### Skill Categories

- Programming Languages
- Frontend Frameworks
- Backend Frameworks
- Databases
- Cloud Platforms
- AI/ML
- DevOps
- Tools & Libraries
- Soft Skills
- Data Engineering
- Mobile Development
- Testing
- Security

## Usage

### Basic Usage (Backward Compatible)

```python
from preprocessing.skill_extractor import advanced_skill_extractor

# Returns list of canonical skill names (backward compatible)
# Uses regex-based extraction by default (fast, local processing)
skills = advanced_skill_extractor(resume_text)
```

### Advanced Usage with Full Metadata

```python
from preprocessing.skill_extraction_pipeline import extract_skills

# Returns structured output with metadata
# Uses regex-based extraction by default (fast, local processing)
result = extract_skills(resume_text)

# Access extracted skills
skills = result["extracted_skills"]

# Access categorized skills
categorized = result["categorized_skills"]
# {"Programming Languages": ["Python", "JavaScript"], ...}

# Access metadata
confidence = result["confidence_score"]
method = result["extraction_method"]  # "regex" by default
count = result["skill_count"]
```

### Enable LLM for Enhanced Accuracy

```python
# Enable LLM extraction for improved accuracy (slower)
result = extract_skills(resume_text, enable_llm=True)
# method will be "regex+llm"
```

### Use LLM for Categorization

```python
from preprocessing.skill_extraction_pipeline import SkillExtractionPipeline

# Enable LLM for both extraction and categorization
pipeline = SkillExtractionPipeline(enable_llm=True, use_llm_categorization=True)
result = pipeline.extract(resume_text)
# Categorization will be done by LLM instead of rules
```

## Return Value Structure

```python
{
    "extracted_skills": ["Python", "JavaScript", "React", "Docker"],
    "categorized_skills": {
        "Programming Languages": ["Python", "JavaScript"],
        "Frontend Frameworks": ["React"],
        "DevOps": ["Docker"]
    },
    "confidence_score": 87.5,
    "extraction_method": "regex+llm",
    "raw_skills": ["Python", "js", "ReactJS", "Docker"],
    "skill_count": 4
}
```

## Skill Normalization

The pipeline automatically normalizes skills to canonical forms:

| Input | Canonical | Confidence |
|-------|-----------|------------|
| JS | JavaScript | 0.8 |
| ReactJS | React | 0.8 |
| node | Node.js | 0.8 |
| ml | Machine Learning | 0.8 |
| Python | Python | 1.0 |
| aws | AWS | 0.8 |

## Integration with Streamlit

The Streamlit app now displays:

- **Total Skills**: Count of extracted skills
- **Extraction Confidence**: Overall confidence score (0-100)
- **Skills by Category**: Expandable sections for each category

## Benefits

### Before (Dictionary-Based)
- Limited to predefined skill list
- No alias handling
- No categorization
- Missed variations and synonyms
- No confidence scoring

### After (Multi-Method Pipeline)
- 200+ skill aliases mapped
- Regex + LLM extraction
- Automatic normalization
- 14 skill categories
- Confidence scoring
- Context-aware extraction
- Production-ready error handling

## Performance

### Speed
- Regex-only (default): ~10ms
- Regex + LLM: ~2-5s (depends on text length)
- LLM categorization: ~3-6s

### Recommendations
- Use regex-only (default) for fast, local processing
- Enable LLM for enhanced accuracy when needed
- Disable LLM for batch processing or speed-critical applications
- The pipeline automatically merges results when LLM is enabled

## Extensibility

### Adding New Skills

Edit `skill_normalizer.py`:

```python
SKILL_ALIASES = {
    # Add new aliases
    "new_skill_alias": "Canonical Skill Name",
}
```

### Adding New Categories

Edit `skill_categorizer.py`:

```python
SKILL_CATEGORIES = {
    "New Category": {
        "Skill1", "Skill2", "Skill3"
    },
}
```

### Adding New Extraction Methods

Create a new extractor module and integrate into `skill_extraction_pipeline.py`:

```python
def extract_skills_with_custom_method(text):
    # Your extraction logic
    return [(skill, confidence)]
```

## Error Handling

The pipeline handles errors gracefully:
- LLM failures fall back to regex extraction
- Individual method failures don't stop the pipeline
- Returns best available extraction
- Provides detailed error information in metadata

## Dependencies

All dependencies are already in `requirements.txt`:
- `google-generativeai` - LLM extraction
- Existing NLP libraries for regex processing

## Future Enhancements

- Add more skill aliases (target: 500+)
- Support for custom skill taxonomies
- Skill proficiency level detection
- Skill relevance scoring for specific roles
- Parallel extraction for faster processing
- Caching for repeated extractions
- Skill trend analysis
