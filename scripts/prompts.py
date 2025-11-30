#!/usr/bin/env python3
"""
Prompt Templates for Different Answer Modes.

This module defines prompt templates for different contexts:
- exam: Formal exam-style answers with clear points
- local: Kenyan context with local examples
- global: International context with global examples
- mixed: Balance of both Kenyan and international examples

Each template is designed to guide the LLM to produce answers
appropriate for KCA University students.
"""

from typing import Dict, Optional


# Prompt templates for different modes
PROMPT_TEMPLATES: Dict[str, str] = {
    "exam": """You are an expert tutor helping a KCA University student prepare for exams.

INSTRUCTIONS:
- Answer the question as if it were an exam question
- Give points clearly and concisely
- Use proper formatting with numbered points where applicable
- If relevant, reference the past paper context
- Keep the answer focused and to the point
- Do not include unnecessary explanations
- Aim for clarity over length

QUESTION:
{question}

ANSWER:""",

    "local": """You are an expert tutor familiar with Kenyan education and KCA University curriculum.

INSTRUCTIONS:
- Answer using Kenyan context and real Kenyan examples
- Include details relevant to KCA University students
- Reference Kenyan institutions, companies, or scenarios where appropriate
- Make the answer relatable to Kenyan students
- Explain concepts using local context
- Keep the answer clear and concise

QUESTION:
{question}

ANSWER:""",

    "global": """You are an expert tutor with international knowledge.

INSTRUCTIONS:
- Answer using international examples and broader context
- Reference global best practices and international standards
- Include examples from different countries and contexts
- Explain concepts using worldwide perspectives
- Make the answer comprehensive and globally relevant
- Keep the answer clear and concise

QUESTION:
{question}

ANSWER:""",

    "mixed": """You are an expert tutor helping a KCA University student.

INSTRUCTIONS:
- Balance Kenyan and international examples in your answer
- Start with local context relevant to KCA students
- Then provide international perspective for broader understanding
- Use both local and global examples where applicable
- Make the answer comprehensive yet concise
- Ensure clarity throughout

QUESTION:
{question}

ANSWER:"""
}


def get_prompt_template(mode: str) -> Optional[str]:
    """
    Get the prompt template for a given mode.
    
    Args:
        mode: Answer mode ('exam', 'local', 'global', 'mixed')
    
    Returns:
        Prompt template string, or None if mode is invalid
    """
    return PROMPT_TEMPLATES.get(mode)


def format_prompt(question: str, mode: str = "exam") -> Optional[str]:
    """
    Format a question with the appropriate prompt template.
    
    Args:
        question: The question to format
        mode: Answer mode ('exam', 'local', 'global', 'mixed')
    
    Returns:
        Formatted prompt string, or None if mode is invalid
    """
    template = get_prompt_template(mode)
    if template is None:
        return None
    
    return template.format(question=question)


def get_available_modes() -> list:
    """
    Get list of available answer modes.
    
    Returns:
        List of mode names
    """
    return list(PROMPT_TEMPLATES.keys())


def validate_mode(mode: str) -> bool:
    """
    Check if a mode is valid.
    
    Args:
        mode: Mode name to validate
    
    Returns:
        True if mode is valid, False otherwise
    """
    return mode in PROMPT_TEMPLATES


if __name__ == "__main__":
    # Test prompt templates
    print("=" * 60)
    print("Available Prompt Templates")
    print("=" * 60)
    
    test_question = "What is object-oriented programming?"
    
    for mode in get_available_modes():
        print(f"\n{'='*60}")
        print(f"Mode: {mode.upper()}")
        print(f"{'='*60}")
        prompt = format_prompt(test_question, mode)
        print(prompt)
        print()
