#!/usr/bin/env python3
"""
Helper script to manually fix 'Unknown' unit codes.

This script provides tools to:
1. Export Unknown unit questions for manual review
2. Create a mapping file to fix unit codes
3. Apply fixes to the dataset
"""

import json
import os
from pathlib import Path
from collections import defaultdict

# Get project root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
INPUT_FILE = os.path.join(project_root, "data", "past_questions_deduplicated.json")
UNKNOWN_EXPORT = os.path.join(project_root, "data", "unknown_units_for_review.json")
UNIT_MAPPING = os.path.join(project_root, "data", "unit_code_mapping.json")
OUTPUT_FILE = os.path.join(project_root, "data", "past_questions_fixed.json")


def export_unknown_units():
    """Export all Unknown unit questions for manual review."""
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    unknown_questions = []
    for i, q in enumerate(questions):
        if q.get('unit') == 'Unknown':
            unknown_questions.append({
                'index': i,
                'year': q.get('year'),
                'source_file': q.get('source_file'),
                'question_number': q.get('question_number'),
                'course': q.get('course'),
                'question_preview': q.get('question', '')[:200] + '...',
                'full_question': q.get('question'),
                'current_unit': 'Unknown',
                'suggested_unit': 'ENTER_UNIT_CODE_HERE'
            })
    
    # Group by source file for easier review
    by_source = defaultdict(list)
    for q in unknown_questions:
        by_source[q['source_file']].append(q)
    
    export_data = {
        'total_unknown': len(unknown_questions),
        'by_source_file': dict(by_source),
        'instructions': [
            '1. Review each question and identify the correct unit code',
            '2. Replace "ENTER_UNIT_CODE_HERE" with the actual unit code',
            '3. Save this file and run: python3 apply_unit_fixes.py',
            '4. The script will update the main dataset'
        ]
    }
    
    with open(UNKNOWN_EXPORT, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Exported {len(unknown_questions)} Unknown unit questions to {UNKNOWN_EXPORT}")
    print(f"\nGrouped by source file:")
    for source, items in sorted(by_source.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {source}: {len(items)} questions")


def create_mapping_template():
    """Create a template mapping file for unit code corrections."""
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    # Group Unknown units by source file
    by_source = defaultdict(list)
    for i, q in enumerate(questions):
        if q.get('unit') == 'Unknown':
            by_source[q.get('source_file')].append({
                'index': i,
                'year': q.get('year'),
                'question_number': q.get('question_number')
            })
    
    # Create mapping template
    mapping = {
        'instructions': [
            'This file maps question indices to their correct unit codes',
            'Format: "index": "UNIT_CODE"',
            'Example: "42": "BBIT106"',
            'Leave as null if unit code is unknown'
        ],
        'mappings': {}
    }
    
    for source, items in by_source.items():
        mapping['mappings'][source] = {}
        for item in items:
            mapping['mappings'][source][str(item['index'])] = None
    
    with open(UNIT_MAPPING, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Created mapping template at {UNIT_MAPPING}")
    print(f"  Total Unknown units to map: {sum(len(v) for v in mapping['mappings'].values())}")


def apply_unit_fixes(mapping_file=UNIT_MAPPING):
    """Apply unit code fixes from mapping file."""
    if not os.path.exists(mapping_file):
        print(f"❌ Mapping file not found: {mapping_file}")
        return False
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    with open(mapping_file, 'r', encoding='utf-8') as f:
        mapping_data = json.load(f)
    
    mappings = mapping_data.get('mappings', {})
    fixed_count = 0
    
    # Apply fixes
    for source, index_mapping in mappings.items():
        for index_str, unit_code in index_mapping.items():
            if unit_code is not None:
                index = int(index_str)
                if index < len(questions):
                    old_unit = questions[index].get('unit')
                    questions[index]['unit'] = unit_code
                    fixed_count += 1
                    print(f"  Fixed index {index}: {old_unit} → {unit_code}")
    
    # Save fixed dataset
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Fixed {fixed_count} unit codes")
    print(f"✓ Saved to {OUTPUT_FILE}")
    
    return True


def show_statistics():
    """Show current statistics."""
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    unknown_count = sum(1 for q in questions if q.get('unit') == 'Unknown')
    known_count = len(questions) - unknown_count
    
    print("\n" + "=" * 60)
    print("UNIT CODE STATISTICS")
    print("=" * 60)
    print(f"Total questions: {len(questions)}")
    print(f"Known unit codes: {known_count} ({known_count/len(questions)*100:.1f}%)")
    print(f"Unknown unit codes: {unknown_count} ({unknown_count/len(questions)*100:.1f}%)")
    
    # Show known units
    units = defaultdict(int)
    for q in questions:
        unit = q.get('unit', 'Unknown')
        if unit != 'Unknown':
            units[unit] += 1
    
    print(f"\nKnown units:")
    for unit, count in sorted(units.items(), key=lambda x: x[1], reverse=True):
        print(f"  {unit}: {count}")


def main():
    """Main workflow."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 fix_unknown_units.py <command>")
        print("\nCommands:")
        print("  export     - Export Unknown units for manual review")
        print("  template   - Create mapping template")
        print("  apply      - Apply fixes from mapping file")
        print("  stats      - Show current statistics")
        print("\nWorkflow:")
        print("  1. python3 fix_unknown_units.py export")
        print("  2. Review and manually fill in unit codes")
        print("  3. python3 fix_unknown_units.py apply")
        return
    
    command = sys.argv[1]
    
    if command == "export":
        export_unknown_units()
    elif command == "template":
        create_mapping_template()
    elif command == "apply":
        apply_unit_fixes()
    elif command == "stats":
        show_statistics()
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
