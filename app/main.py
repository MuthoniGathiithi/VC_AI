#!/usr/bin/env python3
"""
I-TUTOR Main Application.

This module provides the core API for the intelligent tutoring system:
- get_unit(): Retrieve questions for a specific unit
- get_answer(): Generate answers using MCP and LLM
- generate_cat_quiz(): Create random quizzes from past papers
- CLI interface for backend testing

Design Principles:
- No personalization or memory storage
- Content-based and mode-based answers only
- Modular design for easy integration with web UI
- Comprehensive logging for debugging
"""

import sys
import os
import random
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.load_data import load_questions, QuestionLoader
from mcp.client import MCPClient
from scripts.prompts import get_available_modes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ITutorApp:
    """
    Main I-TUTOR Application.
    
    Provides core functionality for question retrieval, answer generation,
    and quiz creation. No personalization or memory storage.
    
    Attributes:
        question_loader (QuestionLoader): Loads and manages questions
        mcp_client (MCPClient): Routes questions to LLM
        default_mode (str): Default answer mode
    """
    
    def __init__(self, default_mode: str = "exam"):
        """
        Initialize I-TUTOR application.
        
        Args:
            default_mode: Default answer mode (exam, local, global, mixed)
        """
        logger.info("Initializing I-TUTOR Application")
        
        # Initialize question loader
        try:
            self.question_loader = load_questions()
            logger.info(f"✓ Loaded {len(self.question_loader.get_all_questions())} questions")
        except Exception as e:
            logger.error(f"Failed to load questions: {e}")
            raise
        
        # Initialize MCP client
        try:
            self.mcp_client = MCPClient(default_mode=default_mode)
            logger.info("✓ MCP Client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize MCP client: {e}")
            raise
        
        self.default_mode = default_mode
    
    def get_unit(self, unit_name: str) -> List[Dict]:
        """
        Get all questions for a specific unit.
        
        Args:
            unit_name: Unit code (e.g., "BBIT106", "ISO100")
        
        Returns:
            List of question dictionaries for the unit
        
        Example:
            >>> app = ITutorApp()
            >>> questions = app.get_unit("BBIT106")
            >>> print(f"Found {len(questions)} questions")
        """
        logger.info(f"Retrieving questions for unit: {unit_name}")
        
        questions = self.question_loader.filter_by_unit(unit_name)
        
        if not questions:
            logger.warning(f"No questions found for unit: {unit_name}")
        else:
            logger.info(f"Found {len(questions)} questions for {unit_name}")
        
        return questions
    
    def get_answer(
        self,
        question: str,
        mode: str = None,
        context: str = None
    ) -> Optional[str]:
        """
        Generate an answer for a question using MCP and LLM.
        
        This is the main method for getting answers. It:
        1. Validates the mode
        2. Optionally includes context (for RAG)
        3. Routes to MCP client
        4. Returns the generated answer
        
        Args:
            question: The question to answer
            mode: Answer mode (exam, local, global, mixed)
                  If None, uses default_mode
            context: Optional context from past papers (for RAG)
        
        Returns:
            Generated answer string, or None if generation fails
        
        Example:
            >>> app = ITutorApp()
            >>> answer = app.get_answer(
            ...     "What is OOP?",
            ...     mode="exam"
            ... )
            >>> print(answer)
        """
        # Use default mode if not specified
        if mode is None:
            mode = self.default_mode
        
        logger.info(f"Generating answer in '{mode}' mode")
        
        # Use MCP client to generate answer
        if context:
            answer = self.mcp_client.answer_question_with_context(
                question,
                context=context,
                mode=mode
            )
        else:
            answer = self.mcp_client.answer_question(question, mode=mode)
        
        if answer:
            logger.info(f"Answer generated successfully ({len(answer)} chars)")
        else:
            logger.warning("Failed to generate answer")
        
        return answer
    
    def generate_cat_quiz(
        self,
        unit: str,
        num_questions: int = 5
    ) -> Optional[List[Dict]]:
        """
        Generate a random CAT (Continuous Assessment Test) quiz from past papers.
        
        This method:
        1. Retrieves all questions for the unit
        2. Randomly selects num_questions
        3. Returns them as a quiz
        
        Args:
            unit: Unit code (e.g., "BBIT106")
            num_questions: Number of questions to include (default: 5)
        
        Returns:
            List of quiz questions, or None if unit has insufficient questions
        
        Example:
            >>> app = ITutorApp()
            >>> quiz = app.generate_cat_quiz("BBIT106", num_questions=3)
            >>> for i, q in enumerate(quiz, 1):
            ...     print(f"Q{i}: {q['question'][:100]}...")
        """
        logger.info(f"Generating CAT quiz for {unit} ({num_questions} questions)")
        
        # Get all questions for the unit
        unit_questions = self.get_unit(unit)
        
        if not unit_questions:
            logger.warning(f"No questions available for {unit}")
            return None
        
        # Check if we have enough questions
        if len(unit_questions) < num_questions:
            logger.warning(
                f"Unit {unit} has only {len(unit_questions)} questions, "
                f"requested {num_questions}"
            )
            num_questions = len(unit_questions)
        
        # Randomly select questions
        quiz_questions = random.sample(unit_questions, num_questions)
        
        # Add quiz metadata
        quiz = {
            "unit": unit,
            "num_questions": len(quiz_questions),
            "generated_at": datetime.now().isoformat(),
            "questions": quiz_questions
        }
        
        logger.info(f"Generated CAT quiz with {len(quiz_questions)} questions")
        
        return quiz
    
    def get_available_units(self) -> List[str]:
        """
        Get list of all available units.
        
        Returns:
            List of unit codes
        """
        units = self.question_loader.get_unique_units()
        return sorted(list(units))
    
    def get_available_years(self) -> List[str]:
        """
        Get list of all available years.
        
        Returns:
            List of years
        """
        years = self.question_loader.get_unique_years()
        return sorted(list(years))
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about the question database.
        
        Returns:
            Dictionary with statistics
        """
        return self.question_loader.get_statistics()
    
    def check_connection(self) -> bool:
        """
        Check if Ollama server is running and accessible.
        
        Returns:
            True if connection successful, False otherwise
        """
        return self.mcp_client.check_connection()


# Global app instance (lazy loaded)
_app_instance: Optional[ITutorApp] = None


def get_app(default_mode: str = "exam") -> ITutorApp:
    """
    Get or create the global app instance.
    
    Args:
        default_mode: Default answer mode
    
    Returns:
        ITutorApp instance
    """
    global _app_instance
    
    if _app_instance is None:
        _app_instance = ITutorApp(default_mode=default_mode)
    
    return _app_instance


def cli_interface():
    """
    Command-line interface for backend testing.
    
    Allows users to:
    - List available units
    - Get questions for a unit
    - Get answers to questions
    - Generate quizzes
    """
    
    print("\n" + "=" * 80)
    print("I-TUTOR Backend CLI")
    print("=" * 80)
    
    # Initialize app
    try:
        app = get_app()
    except Exception as e:
        print(f"❌ Failed to initialize app: {e}")
        return
    
    # Check connection
    print("\nChecking Ollama connection...")
    if not app.check_connection():
        print("⚠️  Warning: Cannot connect to Ollama server")
        print("   Some features may not work. Make sure Ollama is running:")
        print("   $ ollama serve")
    else:
        print("✓ Connected to Ollama")
    
    # Main CLI loop
    while True:
        print("\n" + "-" * 80)
        print("Options:")
        print("  1. List available units")
        print("  2. Get questions for a unit")
        print("  3. Get answer to a question")
        print("  4. Generate CAT quiz")
        print("  5. Show statistics")
        print("  6. Exit")
        print("-" * 80)
        
        choice = input("Enter choice (1-6): ").strip()
        
        if choice == "1":
            # List units
            units = app.get_available_units()
            print(f"\nAvailable units ({len(units)}):")
            for unit in units:
                questions = app.get_unit(unit)
                print(f"  - {unit}: {len(questions)} questions")
        
        elif choice == "2":
            # Get questions for unit
            unit = input("Enter unit code (e.g., BBIT106): ").strip().upper()
            questions = app.get_unit(unit)
            
            if questions:
                print(f"\nFound {len(questions)} questions for {unit}:")
                for i, q in enumerate(questions[:3], 1):
                    print(f"\n  Q{i} ({q.get('year')}):")
                    print(f"  {q.get('question', '')[:100]}...")
                if len(questions) > 3:
                    print(f"\n  ... and {len(questions) - 3} more questions")
            else:
                print(f"No questions found for {unit}")
        
        elif choice == "3":
            # Get answer
            question = input("Enter question: ").strip()
            if not question:
                print("Question cannot be empty")
                continue
            
            mode = input("Enter mode (exam/local/global/mixed) [exam]: ").strip().lower()
            if not mode:
                mode = "exam"
            
            print(f"\nGenerating answer in {mode} mode...")
            answer = app.get_answer(question, mode=mode)
            
            if answer:
                print(f"\n✓ Answer:")
                print(f"{answer}")
            else:
                print("❌ Failed to generate answer")
        
        elif choice == "4":
            # Generate quiz
            unit = input("Enter unit code (e.g., BBIT106): ").strip().upper()
            num_q = input("Number of questions [5]: ").strip()
            
            try:
                num_q = int(num_q) if num_q else 5
            except ValueError:
                print("Invalid number")
                continue
            
            quiz = app.generate_cat_quiz(unit, num_questions=num_q)
            
            if quiz:
                print(f"\n✓ Generated CAT Quiz for {unit}:")
                print(f"  Questions: {quiz['num_questions']}")
                print(f"  Generated: {quiz['generated_at']}")
                print(f"\n  Questions:")
                for i, q in enumerate(quiz['questions'], 1):
                    print(f"    Q{i}: {q.get('question', '')[:80]}...")
            else:
                print(f"Failed to generate quiz for {unit}")
        
        elif choice == "5":
            # Show statistics
            stats = app.get_statistics()
            print(f"\n📊 Database Statistics:")
            print(f"  Total questions: {stats['total_questions']}")
            print(f"  Unique units: {stats['unique_units']}")
            print(f"  Unique years: {stats['unique_years']}")
            print(f"\n  Questions per unit (top 5):")
            for unit, count in sorted(
                stats['questions_per_unit'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]:
                print(f"    {unit}: {count}")
        
        elif choice == "6":
            print("\nGoodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    # Run CLI interface
    try:
        cli_interface()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)
