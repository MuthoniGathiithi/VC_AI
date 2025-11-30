#!/usr/bin/env python3
"""
MCP Client for Question Routing and Answer Generation.

This module implements the MCPClient class which:
1. Accepts a question and answer mode
2. Selects the appropriate prompt template
3. Sends the formatted prompt to the local LLM
4. Returns the generated answer

Modes:
- exam: Formal exam-style answers
- local: Kenyan context with local examples
- global: International context
- mixed: Balance of both contexts
"""

import sys
import os
from typing import Optional, Dict

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.ollama_client import OllamaClient, query_model
from scripts.prompts import format_prompt, validate_mode, get_available_modes
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPClient:
    """
    MCP (Model Coordination Protocol) Client.
    
    Routes questions to appropriate answer modes and coordinates
    with the local Ollama LLM for response generation.
    
    Attributes:
        ollama_client (OllamaClient): Client for Ollama communication
        default_mode (str): Default answer mode
        temperature_map (dict): Temperature settings per mode
    """
    
    def __init__(
        self,
        model: str = "llama2",
        default_mode: str = "exam",
        base_url: str = "http://localhost:11434"
    ):
        """
        Initialize MCP Client.
        
        Args:
            model: LLM model name (default: llama2)
            default_mode: Default answer mode (default: exam)
            base_url: Ollama server URL
        """
        self.ollama_client = OllamaClient(base_url=base_url, model=model)
        self.default_mode = default_mode
        
        # Temperature settings per mode
        # Lower temp = more focused/deterministic
        # Higher temp = more creative/varied
        self.temperature_map = {
            "exam": 0.5,      # Lower for precise exam answers
            "local": 0.7,     # Medium for contextual answers
            "global": 0.7,    # Medium for varied examples
            "mixed": 0.6      # Medium-low for balanced answers
        }
        
        logger.info(f"MCPClient initialized with model: {model}, mode: {default_mode}")
    
    def answer_question(
        self,
        question: str,
        mode: str = None,
        temperature: float = None
    ) -> Optional[str]:
        """
        Generate an answer for a question in the specified mode.
        
        This is the main method that:
        1. Validates the mode
        2. Formats the question with appropriate prompt template
        3. Sends to LLM with appropriate temperature
        4. Returns the generated answer
        
        Args:
            question: The question to answer
            mode: Answer mode ('exam', 'local', 'global', 'mixed')
                  If None, uses default_mode
            temperature: Sampling temperature (0.0-1.0)
                        If None, uses temperature_map for mode
        
        Returns:
            Generated answer string, or None if generation fails
        """
        # Use default mode if not specified
        if mode is None:
            mode = self.default_mode
        
        # Validate mode
        if not validate_mode(mode):
            logger.error(f"Invalid mode: {mode}. Available: {get_available_modes()}")
            return None
        
        # Use default temperature for mode if not specified
        if temperature is None:
            temperature = self.temperature_map.get(mode, 0.7)
        
        logger.info(f"Answering question in '{mode}' mode (temp={temperature})")
        
        # Format question with appropriate prompt template
        formatted_prompt = format_prompt(question, mode)
        if formatted_prompt is None:
            logger.error(f"Failed to format prompt for mode: {mode}")
            return None
        
        # Send to LLM and get response
        answer = self.ollama_client.query_model(
            formatted_prompt,
            temperature=temperature
        )
        
        if answer:
            logger.info(f"Successfully generated answer ({len(answer)} chars)")
        else:
            logger.warning("Failed to generate answer from LLM")
        
        return answer
    
    def answer_question_with_context(
        self,
        question: str,
        context: str = None,
        mode: str = None
    ) -> Optional[str]:
        """
        Generate an answer with optional context (for RAG integration).
        
        Args:
            question: The question to answer
            context: Optional context from past papers or other sources
            mode: Answer mode
        
        Returns:
            Generated answer string, or None if generation fails
        """
        # Combine context with question if provided
        if context:
            combined_prompt = f"CONTEXT:\n{context}\n\nQUESTION:\n{question}"
        else:
            combined_prompt = question
        
        return self.answer_question(combined_prompt, mode)
    
    def batch_answer_questions(
        self,
        questions: list,
        mode: str = None
    ) -> Dict[str, Optional[str]]:
        """
        Generate answers for multiple questions.
        
        Args:
            questions: List of questions to answer
            mode: Answer mode for all questions
        
        Returns:
            Dictionary mapping questions to answers
        """
        results = {}
        
        for i, question in enumerate(questions, 1):
            logger.info(f"Processing question {i}/{len(questions)}")
            answer = self.answer_question(question, mode)
            results[question] = answer
        
        return results
    
    def check_connection(self) -> bool:
        """
        Check if Ollama server is running and accessible.
        
        Returns:
            True if connection successful, False otherwise
        """
        return self.ollama_client.check_connection()
    
    def get_available_modes(self) -> list:
        """
        Get list of available answer modes.
        
        Returns:
            List of mode names
        """
        return get_available_modes()


if __name__ == "__main__":
    # Test MCPClient
    print("=" * 70)
    print("Testing MCP Client - Exam Mode")
    print("=" * 70)
    
    # Initialize client
    client = MCPClient(default_mode="exam")
    
    # Check connection
    print("\n1. Checking Ollama connection...")
    if not client.check_connection():
        print("❌ Cannot connect to Ollama server")
        print("   Make sure Ollama is running: ollama serve")
        exit(1)
    
    print("✓ Connected to Ollama")
    
    # Test question
    print("\n2. Testing question answering...")
    test_question = "What is the difference between a class and an object in object-oriented programming?"
    
    print(f"\nQuestion: {test_question}")
    print("\nGenerating answer in EXAM mode...")
    print("-" * 70)
    
    answer = client.answer_question(test_question, mode="exam")
    
    if answer:
        print("ANSWER:")
        print(answer)
        print("-" * 70)
        print("✓ Test successful!")
    else:
        print("❌ Failed to generate answer")
    
    # Test different modes
    print("\n3. Testing different modes...")
    modes = ["local", "global", "mixed"]
    
    for mode in modes:
        print(f"\n   Testing {mode.upper()} mode...")
        answer = client.answer_question(test_question, mode=mode)
        if answer:
            print(f"   ✓ {mode} mode works")
        else:
            print(f"   ❌ {mode} mode failed")
