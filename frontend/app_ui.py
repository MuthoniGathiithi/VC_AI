#!/usr/bin/env python3
"""
I-TUTOR Streamlit UI - Phase 8 MVP

A clean, modern Streamlit interface for the I-TUTOR intelligent tutoring system.
Allows users to ask questions about KCA University past exam papers and get
AI-powered answers using RAG (Retrieval-Augmented Generation) and MCP routing.

Features:
- Question input with mode selection
- Real-time answer generation
- Past paper context retrieval
- Clean, professional UI with indigo/white/black theme
- Render deployment ready

Author: I-TUTOR Team
Date: November 30, 2025
"""

import streamlit as st
import sys
import os
from typing import Optional, List, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import backend modules
try:
    from mcp.client import MCPClient
    from scripts.rag import initialize_rag_system
    from scripts.load_data import load_questions
    from mcp.orchestrator import MCPOrchestrator
except ImportError as e:
    logger.error(f"Failed to import backend modules: {e}")
    st.error("Failed to load backend modules. Please check installation.")
    sys.exit(1)


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="I-TUTOR",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for indigo/white/black theme
st.markdown("""
    <style>
    /* Main theme colors */
    :root {
        --indigo: #4F46E5;
        --indigo-dark: #4338CA;
        --white: #FFFFFF;
        --black: #1F2937;
        --gray-light: #F3F4F6;
        --gray-dark: #6B7280;
    }
    
    /* Main container */
    .main {
        background-color: var(--white);
        color: var(--black);
    }
    
    /* Header styling */
    .header-title {
        color: var(--indigo);
        font-size: 2.5em;
        font-weight: 700;
        margin-bottom: 0.5em;
    }
    
    .header-subtitle {
        color: var(--gray-dark);
        font-size: 1.1em;
        margin-bottom: 1.5em;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: var(--indigo);
        color: var(--white);
        border: none;
        border-radius: 0.5em;
        padding: 0.75em 2em;
        font-weight: 600;
        transition: background-color 0.3s;
    }
    
    .stButton > button:hover {
        background-color: var(--indigo-dark);
    }
    
    /* Input styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border: 2px solid var(--indigo);
        border-radius: 0.5em;
        padding: 0.75em;
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div > select {
        border: 2px solid var(--indigo);
        border-radius: 0.5em;
    }
    
    /* Card styling */
    .card {
        background-color: var(--gray-light);
        border-left: 4px solid var(--indigo);
        padding: 1.5em;
        border-radius: 0.5em;
        margin: 1em 0;
    }
    
    /* Success message */
    .success-box {
        background-color: #ECFDF5;
        border-left: 4px solid #10B981;
        padding: 1em;
        border-radius: 0.5em;
    }
    
    /* Info message */
    .info-box {
        background-color: #EFF6FF;
        border-left: 4px solid var(--indigo);
        padding: 1em;
        border-radius: 0.5em;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background-color: var(--gray-light);
    }
    </style>
""", unsafe_allow_html=True)


# ============================================================================
# INITIALIZATION & CACHING
# ============================================================================

@st.cache_resource
def initialize_backend():
    """
    Initialize backend components (MCP client, RAG system).
    Uses Streamlit caching to avoid re-initialization on every run.
    
    Returns:
        Tuple of (mcp_client, rag_system, question_loader)
    """
    try:
        logger.info("Initializing backend components...")
        
        # Initialize MCP client
        mcp_client = MCPClient(default_mode="local")
        logger.info("✓ MCP client initialized")
        
        # Initialize RAG system
        rag_system = initialize_rag_system(force_rebuild=False)
        logger.info("✓ RAG system initialized")
        
        # Initialize question loader
        question_loader = load_questions()
        logger.info("✓ Question loader initialized")
        
        return mcp_client, rag_system, question_loader
    
    except Exception as e:
        logger.error(f"Failed to initialize backend: {e}")
        raise


@st.cache_resource
def initialize_orchestrator():
    """
    Initialize MCP Orchestrator for intelligent RAG routing.
    
    Returns:
        MCPOrchestrator instance
    """
    try:
        logger.info("Initializing orchestrator...")
        orchestrator = MCPOrchestrator()
        logger.info("✓ Orchestrator initialized")
        return orchestrator
    except Exception as e:
        logger.error(f"Failed to initialize orchestrator: {e}")
        return None


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_available_modes() -> List[str]:
    """
    Get list of available answer modes.
    
    Returns:
        List of mode names
    """
    return ["exam", "local", "global", "mixed"]


def format_answer_display(answer: str, max_length: int = 2000) -> str:
    """
    Format answer for display in UI.
    
    Args:
        answer: Raw answer text
        max_length: Maximum length to display
    
    Returns:
        Formatted answer
    """
    if not answer:
        return "No answer generated."
    
    # Truncate if too long
    if len(answer) > max_length:
        return answer[:max_length] + "\n\n[Answer truncated for display]"
    
    return answer


def format_retrieved_questions(questions: List[Dict]) -> str:
    """
    Format retrieved past paper questions for display.
    
    Args:
        questions: List of question dictionaries
    
    Returns:
        Formatted string for display
    """
    if not questions:
        return "No relevant past papers found."
    
    formatted = "📚 **Relevant Past Papers:**\n\n"
    
    for i, q in enumerate(questions, 1):
        unit = q.get("unit", "Unknown")
        year = q.get("year", "Unknown")
        similarity = q.get("similarity_score", 0)
        question_text = q.get("question", "")[:150]
        
        formatted += f"**[{i}] {unit} ({year})** - Relevance: {similarity:.0%}\n"
        formatted += f"> {question_text}...\n\n"
    
    return formatted


def get_unit_statistics(question_loader) -> Dict:
    """
    Get statistics about available units.
    
    Args:
        question_loader: QuestionLoader instance
    
    Returns:
        Dictionary with unit statistics
    """
    try:
        all_questions = question_loader.get_all_questions()
        
        # Count questions per unit
        units = {}
        for q in all_questions:
            unit = q.get("unit", "Unknown")
            units[unit] = units.get(unit, 0) + 1
        
        return units
    except Exception as e:
        logger.error(f"Failed to get unit statistics: {e}")
        return {}


# ============================================================================
# MAIN UI LAYOUT
# ============================================================================

def main():
    """Main Streamlit application."""
    
    # Initialize backend
    try:
        mcp_client, rag_system, question_loader = initialize_backend()
        orchestrator = initialize_orchestrator()
    except Exception as e:
        st.error(f"Failed to initialize backend: {e}")
        st.info("Please ensure Ollama is running and all dependencies are installed.")
        return
    
    # ========================================================================
    # HEADER
    # ========================================================================
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(
            '<div class="header-title">🎓 I-TUTOR</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="header-subtitle">Intelligent Tutoring System for KCA University</div>',
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""
            <div style="text-align: right; padding-top: 1em;">
                <span style="color: #4F46E5; font-weight: 600;">v0.1.0 MVP</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.divider()
    
    # ========================================================================
    # SIDEBAR - INFORMATION & SETTINGS
    # ========================================================================
    
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        
        # Mode selection
        st.markdown("**Answer Mode**")
        mode = st.selectbox(
            "Select how you want answers formatted:",
            options=get_available_modes(),
            index=1,  # Default to "local"
            help="exam: Formal exam-style | local: Kenyan context | global: International | mixed: Both"
        )
        
        # RAG toggle
        st.markdown("**Retrieval Options**")
        use_rag = st.checkbox(
            "Use past papers context (RAG)",
            value=True,
            help="Retrieve relevant past exam questions to augment answers"
        )
        
        top_k = st.slider(
            "Number of past papers to retrieve:",
            min_value=1,
            max_value=10,
            value=3,
            help="More papers = more context but longer processing"
        )
        
        st.divider()
        
        # Statistics
        st.markdown("### 📊 Database Statistics")
        
        try:
            units = get_unit_statistics(question_loader)
            all_questions = question_loader.get_all_questions()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Questions", len(all_questions))
            with col2:
                st.metric("Units", len(units))
            
            # Unit breakdown
            if units:
                st.markdown("**Questions per Unit:**")
                for unit, count in sorted(units.items(), key=lambda x: x[1], reverse=True)[:5]:
                    st.write(f"• {unit}: {count}")
        
        except Exception as e:
            st.warning(f"Could not load statistics: {e}")
        
        st.divider()
        
        # Help section
        st.markdown("### 💡 How to Use")
        st.markdown("""
        1. **Enter your question** in the text area
        2. **Select answer mode** (default: local)
        3. **Toggle RAG** to use past papers
        4. **Click Submit** to get answer
        5. **View results** with context
        """)
    
    # ========================================================================
    # MAIN CONTENT AREA
    # ========================================================================
    
    # Question input section
    st.markdown("### 📝 Ask a Question")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        question = st.text_area(
            label="Your Question",
            placeholder="e.g., What is object-oriented programming? Explain with examples.",
            height=100,
            help="Ask any question related to KCA University curriculum"
        )
    
    with col2:
        st.markdown("**Mode**")
        st.write(mode)
        st.markdown("**RAG**")
        st.write("✓ On" if use_rag else "✗ Off")
    
    # Submit button
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        submit_button = st.button(
            "🚀 Submit",
            use_container_width=True,
            type="primary"
        )
    
    with col2:
        clear_button = st.button(
            "🔄 Clear",
            use_container_width=True
        )
    
    if clear_button:
        st.rerun()
    
    # ========================================================================
    # ANSWER GENERATION & DISPLAY
    # ========================================================================
    
    if submit_button:
        if not question.strip():
            st.warning("Please enter a question.")
            return
        
        # Show processing status
        with st.spinner("🔄 Processing your question..."):
            try:
                # Step 1: Retrieve past papers if RAG enabled
                retrieved_questions = []
                if use_rag and rag_system:
                    logger.info(f"Retrieving top {top_k} past papers...")
                    retrieved_questions = rag_system.retrieve_notes(
                        question,
                        top_k=top_k,
                        similarity_threshold=0.3
                    )
                    logger.info(f"Retrieved {len(retrieved_questions)} past papers")
                
                # Step 2: Generate answer using MCP + RAG
                logger.info(f"Generating answer in '{mode}' mode...")
                
                if orchestrator and use_rag:
                    # Use orchestrator for intelligent RAG routing
                    answer = orchestrator.answer_question(
                        question,
                        mode=mode,
                        use_rag=True,
                        top_k=top_k
                    )
                else:
                    # Use MCP client directly
                    answer = mcp_client.answer_question(
                        question,
                        mode=mode
                    )
                
                logger.info("Answer generated successfully")
                
                # Display results
                st.success("✅ Answer generated successfully!")
                
                # Create tabs for answer and context
                tab1, tab2 = st.tabs(["📖 Answer", "📚 Context"])
                
                with tab1:
                    st.markdown("### AI Answer")
                    st.markdown(
                        f"""
                        <div class="card">
                        {format_answer_display(answer)}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    # Display metadata
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Answer Length", f"{len(answer)} chars")
                    with col2:
                        st.metric("Mode", mode.capitalize())
                    with col3:
                        st.metric("RAG Used", "Yes" if use_rag else "No")
                
                with tab2:
                    st.markdown("### Retrieved Past Papers")
                    
                    if retrieved_questions:
                        st.markdown(format_retrieved_questions(retrieved_questions))
                        
                        # Show detailed context
                        with st.expander("📋 Detailed Context"):
                            for i, q in enumerate(retrieved_questions, 1):
                                st.markdown(f"**Question {i}**")
                                st.write(f"Unit: {q.get('unit', 'Unknown')}")
                                st.write(f"Year: {q.get('year', 'Unknown')}")
                                st.write(f"Relevance: {q.get('similarity_score', 0):.0%}")
                                st.write(f"Question: {q.get('question', '')}")
                                st.divider()
                    else:
                        st.info("No relevant past papers found for this query.")
            
            except Exception as e:
                logger.error(f"Error generating answer: {e}")
                st.error(f"Error generating answer: {e}")
                st.info("Please ensure Ollama is running and try again.")
    
    # ========================================================================
    # FOOTER
    # ========================================================================
    
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            """
            <div style="text-align: center; color: #6B7280; font-size: 0.9em;">
            <strong>I-TUTOR v0.1.0</strong><br>
            Intelligent Tutoring System
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            """
            <div style="text-align: center; color: #6B7280; font-size: 0.9em;">
            <strong>Powered by</strong><br>
            LLaMA 2 + FAISS + RAG
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            """
            <div style="text-align: center; color: #6B7280; font-size: 0.9em;">
            <strong>KCA University</strong><br>
            School of Technology
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()
