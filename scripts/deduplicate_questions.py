#!/usr/bin/env python3
"""
Deduplicate questions and implement Option 3: Keep canonical version + track sources.

This script:
- Identifies exact duplicate questions
- Keeps one canonical version (earliest year or most complete)
- Merges metadata to track all source PDFs and years
- Generates a clean deduplicated dataset
- Provides analysis of duplicates found
"""

import json
import os
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Tuple

# Get project root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
INPUT_FILE = os.path.join(project_root, "data", "extracted_questions.json")
OUTPUT_FILE = os.path.join(project_root, "data", "past_questions_deduplicated.json")
REPORT_FILE = os.path.join(project_root, "data", "deduplication_report.json")


def load_questions(json_file: str) -> List[Dict]:
    """Load questions from JSON file."""
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def find_duplicates(questions: List[Dict]) -> Dict[str, List[int]]:
    """
    Find exact duplicate questions by comparing question text.
    
    Returns:
        Dict mapping question text to list of indices in original data
    """
    question_texts = defaultdict(list)
    for i, q in enumerate(questions):
        text = q.get('question', '').strip()
        question_texts[text].append(i)
    
    # Return only duplicates (len > 1)
    return {text: indices for text, indices in question_texts.items() if len(indices) > 1}


def select_canonical_version(questions: List[Dict], indices: List[int]) -> Tuple[int, Dict]:
    """
    Select the canonical version from duplicate group.
    
    Priority:
    1. Question with known unit code (not "Unknown")
    2. Earliest year
    3. Most complete metadata
    4. First in list
    
    Returns:
        Tuple of (canonical_index, canonical_question)
    """
    candidates = [(i, questions[i]) for i in indices]
    
    # Sort by priority
    def priority_key(item):
        idx, q = item
        unit = q.get('unit', 'Unknown')
        year = int(q.get('year', 9999)) if q.get('year') else 9999
        has_metadata = 1 if q.get('metadata') else 0
        
        # Lower values = higher priority
        return (
            unit == 'Unknown',  # False (0) if known, True (1) if unknown
            year,                # Earlier years first
            -has_metadata        # Has metadata = -1, no metadata = 0
        )
    
    canonical_idx, canonical_q = min(candidates, key=priority_key)
    return canonical_idx, canonical_q


def merge_sources(questions: List[Dict], indices: List[int]) -> Dict:
    """
    Merge source information from all duplicate instances.
    
    Returns:
        Dict with merged source information
    """
    sources = []
    years = set()
    source_files = set()
    
    for idx in indices:
        q = questions[idx]
        year = q.get('year')
        source_file = q.get('source_file')
        
        if year:
            years.add(str(year))
        if source_file:
            source_files.add(source_file)
        
        sources.append({
            'year': year,
            'source_file': source_file,
            'question_number': q.get('question_number'),
            'original_index': idx
        })
    
    return {
        'source_pdfs': sorted(list(source_files)),
        'years_found': sorted(list(years)),
        'all_sources': sources,
        'duplicate_count': len(indices)
    }


def deduplicate_questions(questions: List[Dict]) -> Tuple[List[Dict], Dict]:
    """
    Deduplicate questions following Option 3 strategy.
    
    Returns:
        Tuple of (deduplicated_questions, deduplication_report)
    """
    duplicates = find_duplicates(questions)
    
    # Track which original indices to keep
    indices_to_keep = set(range(len(questions)))
    deduplicated = []
    report = {
        'total_original': len(questions),
        'total_duplicates_found': len(duplicates),
        'total_duplicate_instances': sum(len(v) - 1 for v in duplicates.values()),
        'duplicate_groups': []
    }
    
    # Process each duplicate group
    for question_text, indices in duplicates.items():
        canonical_idx, canonical_q = select_canonical_version(questions, indices)
        
        # Merge source information
        merged_sources = merge_sources(questions, indices)
        
        # Create enhanced canonical question with merged metadata
        enhanced_q = canonical_q.copy()
        enhanced_q['source_metadata'] = merged_sources
        
        # Update metadata if it exists
        if 'metadata' not in enhanced_q:
            enhanced_q['metadata'] = {}
        enhanced_q['metadata']['source_pdfs'] = merged_sources['source_pdfs']
        enhanced_q['metadata']['years_found'] = merged_sources['years_found']
        enhanced_q['metadata']['is_deduplicated'] = True
        enhanced_q['metadata']['duplicate_count'] = merged_sources['duplicate_count']
        
        deduplicated.append(enhanced_q)
        
        # Mark non-canonical indices for removal
        for idx in indices:
            if idx != canonical_idx:
                indices_to_keep.discard(idx)
        
        # Add to report
        report['duplicate_groups'].append({
            'canonical_index': canonical_idx,
            'canonical_unit': canonical_q.get('unit'),
            'canonical_year': canonical_q.get('year'),
            'duplicate_indices': indices,
            'merged_sources': merged_sources
        })
    
    # Add non-duplicate questions
    for i in sorted(indices_to_keep):
        if i not in [group['canonical_index'] for group in report['duplicate_groups']]:
            q = questions[i].copy()
            if 'metadata' not in q:
                q['metadata'] = {}
            q['metadata']['is_deduplicated'] = False
            deduplicated.append(q)
    
    report['total_after_deduplication'] = len(deduplicated)
    report['questions_removed'] = report['total_original'] - report['total_after_deduplication']
    
    return deduplicated, report


def print_report(report: Dict) -> None:
    """Print deduplication report to console."""
    print("\n" + "=" * 70)
    print("DEDUPLICATION REPORT")
    print("=" * 70)
    
    print(f"\n📊 Summary:")
    print(f"  Total original questions: {report['total_original']}")
    print(f"  Duplicate groups found: {report['total_duplicates_found']}")
    print(f"  Total duplicate instances: {report['total_duplicate_instances']}")
    print(f"  Questions removed: {report['questions_removed']}")
    print(f"  Final dataset size: {report['total_after_deduplication']}")
    
    print(f"\n🔍 Duplicate Groups Details:")
    for i, group in enumerate(report['duplicate_groups'], 1):
        print(f"\n  Group {i}:")
        print(f"    Canonical: Unit={group['canonical_unit']}, Year={group['canonical_year']}")
        print(f"    Duplicate count: {group['merged_sources']['duplicate_count']}")
        print(f"    Source PDFs: {', '.join(group['merged_sources']['source_pdfs'][:2])}...")
        print(f"    Years found: {', '.join(group['merged_sources']['years_found'])}")


def main():
    """Main deduplication workflow."""
    print("Loading questions...")
    questions = load_questions(INPUT_FILE)
    print(f"✓ Loaded {len(questions)} questions")
    
    print("\nDeduplicating questions...")
    deduplicated, report = deduplicate_questions(questions)
    
    print(f"✓ Deduplication complete")
    print_report(report)
    
    # Save deduplicated questions
    print(f"\nSaving deduplicated questions to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(deduplicated, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved {len(deduplicated)} deduplicated questions")
    
    # Save report
    print(f"\nSaving report to {REPORT_FILE}...")
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"✓ Report saved")
    
    print("\n" + "=" * 70)
    print("✅ Deduplication complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
