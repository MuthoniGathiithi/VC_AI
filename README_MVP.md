#UNI_AI  MVP - Intelligent Tutoring System

## Overview

UNI_AI is an intelligent tutoring system for KCA University students, powered by local LLaMA model and past exam papers. The MVP (Minimum Viable Product) includes:

- **Phase 4**: Local AI Model + MCP Routing
- **Phase 5**: Main Application with CLI & Tests

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    UNI_AI Application                      │
│                    (app/main.py)                            │
├─────────────────────────────────────────────────────────────┤
│  - get_unit()           - Get questions by unit             │
│  - get_answer()         - Generate answers using MCP        │
│  - generate_cat_quiz()  - Create random quizzes             │
│  - CLI interface        - Backend testing                   │
├─────────────────────────────────────────────────────────────┤
│                    MCP Client                               │
│                    (mcp/client.py)                          │
│  Routes questions to appropriate answer modes              │
├─────────────────────────────────────────────────────────────┤
│  Ollama Client          │  Question Loader                  │
│  (scripts/ollama_client.py)  (scripts/load_data.py)         │
│  - LLaMA integration    │  - Load past papers               │
│  - Model queries        │  - Filter by unit/year            │
├─────────────────────────────────────────────────────────────┤
│  Prompt Templates       │  Local Ollama Server              │
│  (scripts/prompts.py)   │  (localhost:11434)                │
│  - exam mode            │  - llama2 model                   │
│  - local mode           │  - Running locally                │
│  - global mode          │                                   │
│  - mixed mode           │                                   │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

1. **Python 3.8+**
   ```bash
   python3 --version
   ```

2. **Ollama with LLaMA Model**
   - Install Ollama: https://ollama.ai
   - Pull llama2 model:
     ```bash
     ollama pull llama2
     ```
   - Start Ollama server:
     ```bash
     ollama serve
     ```

3. **Project Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Running the CLI

```bash
python3 app/main.py
```

This starts an interactive CLI where you can:
- List available units
- Get questions for a unit
- Get answers to questions
- Generate CAT quizzes
- View statistics

**Example CLI Session:**
```
I-TUTOR Backend CLI
────────────────────────────────────────────────────────────────────────────────
Options:
  1. List available units
  2. Get questions for a unit
  3. Get answer to a question
  4. Generate CAT quiz
  5. Show statistics
  6. Exit
────────────────────────────────────────────────────────────────────────────────
Enter choice (1-6): 1

Available units (12):
  - BBIT106: 10 questions
  - ISO100: 9 questions
  - BUSS202: 8 questions
  ...
```

## Usage Examples

### Python API

```python
from app.main import ITutorApp

# Initialize app
app = ITutorApp(default_mode="exam")

# Get questions for a unit
questions = app.get_unit("BBIT106")
print(f"Found {len(questions)} questions")

# Get answer to a question
answer = app.get_answer(
    "What is object-oriented programming?",
    mode="exam"
)
print(answer)

# Generate a quiz
quiz = app.generate_cat_quiz("BBIT106", num_questions=5)
for i, q in enumerate(quiz["questions"], 1):
    print(f"Q{i}: {q['question'][:100]}...")
```

### Different Answer Modes

```python
from app.main import ITutorApp

app = ITutorApp()
question = "What is a database?"

# Exam mode - formal, concise answers
exam_answer = app.get_answer(question, mode="exam")

# Local mode - Kenyan context with local examples
local_answer = app.get_answer(question, mode="local")

# Global mode - international examples
global_answer = app.get_answer(question, mode="global")

# Mixed mode - balance of both
mixed_answer = app.get_answer(question, mode="mixed")
```

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test File

```bash
pytest tests/test_main.py -v
```

### Run with Coverage Report

```bash
pytest tests/ --cov=app --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`

### Test Categories

**Unit Tests:**
- `test_get_unit_*` - Test question retrieval
- `test_get_answer_*` - Test answer generation
- `test_generate_cat_quiz_*` - Test quiz generation

**Integration Tests:**
- `TestIntegration` - Complete workflows

**Edge Cases:**
- `TestEdgeCases` - Error handling and special cases

## Project Structure

```
VC_AI/
├── app/
│   ├── __init__.py
│   └── main.py                 # Main application (Phase 5)
├── mcp/
│   ├── __init__.py
│   └── client.py               # MCP routing (Phase 4)
├── scripts/
│   ├── load_data.py            # Question loader
│   ├── ollama_client.py        # Ollama integration (Phase 4)
│   ├── prompts.py              # Prompt templates (Phase 4)
│   └── ...
├── tests/
│   ├── __init__.py
│   └── test_main.py            # Unit tests (Phase 5)
├── data/
│   ├── past_questions_deduplicated.json
│   └── ...
├── phase4_test.py              # Phase 4 demo (Phase 4)
├── requirements.txt
└── README_MVP.md               # This file
```

## Phase 4: Local AI Model + MCP Routing

### Files Created

1. **`scripts/ollama_client.py`**
   - `OllamaClient` class for Ollama communication
   - Methods: `query_model()`, `check_connection()`, `list_models()`

2. **`scripts/prompts.py`**
   - Prompt templates for different modes
   - Functions: `get_prompt_template()`, `format_prompt()`, `validate_mode()`

3. **`mcp/client.py`**
   - `MCPClient` class for question routing
   - Methods: `answer_question()`, `batch_answer_questions()`

4. **`phase4_test.py`**
   - Demonstration of Phase 4 functionality
   - Tests loading, filtering, and answering questions

### Running Phase 4 Test

```bash
python3 phase4_test.py
```

## Phase 5: Main Application with CLI & Tests

### Files Created

1. **`app/main.py`**
   - `ITutorApp` class - main application
   - Methods:
     - `get_unit(unit_name)` - Get questions for a unit
     - `get_answer(question, mode)` - Generate answers
     - `generate_cat_quiz(unit, num_questions)` - Create quizzes
     - `cli_interface()` - Interactive CLI

2. **`tests/test_main.py`**
   - Comprehensive pytest test suite
   - 30+ test cases covering:
     - Unit retrieval
     - Answer generation
     - Quiz generation
     - Edge cases and error handling

### Key Features

✅ **Modular Design**
- Easy to integrate with web UI
- Clean separation of concerns
- Reusable components

✅ **No Personalization**
- Content-based answers only
- Mode-based routing only
- No user data storage

✅ **Comprehensive Logging**
- Track all operations
- Debug information
- Error reporting

✅ **Well-Tested**
- 30+ test cases
- Coverage tracking
- Edge case handling

## API Reference

### ITutorApp

#### `get_unit(unit_name: str) -> List[Dict]`
Get all questions for a specific unit.

**Parameters:**
- `unit_name` (str): Unit code (e.g., "BBIT106")

**Returns:**
- List of question dictionaries

**Example:**
```python
questions = app.get_unit("BBIT106")
```

#### `get_answer(question: str, mode: str = None, context: str = None) -> Optional[str]`
Generate an answer for a question.

**Parameters:**
- `question` (str): The question to answer
- `mode` (str): Answer mode (exam, local, global, mixed). Default: exam
- `context` (str): Optional context for RAG

**Returns:**
- Generated answer string, or None if generation fails

**Example:**
```python
answer = app.get_answer("What is OOP?", mode="exam")
```

#### `generate_cat_quiz(unit: str, num_questions: int = 5) -> Optional[Dict]`
Generate a random CAT quiz from past papers.

**Parameters:**
- `unit` (str): Unit code
- `num_questions` (int): Number of questions (default: 5)

**Returns:**
- Quiz dictionary with questions, or None if unit not found

**Example:**
```python
quiz = app.generate_cat_quiz("BBIT106", num_questions=3)
```

#### `get_available_units() -> List[str]`
Get list of all available units.

**Returns:**
- List of unit codes

#### `get_available_years() -> List[str]`
Get list of all available years.

**Returns:**
- List of years

#### `get_statistics() -> Dict`
Get statistics about the question database.

**Returns:**
- Dictionary with statistics

#### `check_connection() -> bool`
Check if Ollama server is running.

**Returns:**
- True if connected, False otherwise

## Configuration

### Ollama Server

Default configuration:
- **URL**: `http://localhost:11434`
- **Model**: `llama2`
- **Timeout**: 300 seconds

To change, modify in `mcp/client.py`:
```python
client = MCPClient(
    base_url="http://localhost:11434",
    model="llama2"
)
```

### Answer Modes

Defined in `scripts/prompts.py`:

| Mode | Purpose | Temperature |
|------|---------|-------------|
| exam | Formal exam-style answers | 0.5 |
| local | Kenyan context with local examples | 0.7 |
| global | International context | 0.7 |
| mixed | Balance of both contexts | 0.6 |

## Troubleshooting

### "Cannot connect to Ollama server"

**Solution:**
1. Make sure Ollama is running:
   ```bash
   ollama serve
   ```
2. Check if llama2 model is installed:
   ```bash
   ollama list
   ```
3. If not installed, pull it:
   ```bash
   ollama pull llama2
   ```

### "No questions found for unit"

**Solution:**
1. Check available units:
   ```python
   app = ITutorApp()
   print(app.get_available_units())
   ```
2. Make sure unit code is correct (case-insensitive)
3. Check if questions are loaded:
   ```python
   stats = app.get_statistics()
   print(stats['total_questions'])
   ```

### Tests Failing

**Solution:**
1. Make sure Ollama is running (some tests require it)
2. Check that questions are loaded:
   ```bash
   python3 -c "from scripts.load_data import load_questions; l = load_questions()"
   ```
3. Run tests with verbose output:
   ```bash
   pytest tests/ -v -s
   ```

## Performance

### Response Times

- **Question retrieval**: < 100ms
- **Quiz generation**: < 50ms
- **Answer generation**: 10-30 seconds (depends on model)

### Database

- **Total questions**: 172 (deduplicated)
- **Unique units**: 12
- **Unique years**: 8
- **Memory usage**: ~50MB

## Future Enhancements

- [ ] Web UI (Flask/FastAPI)
- [ ] RAG integration for context-aware answers
- [ ] User progress tracking (optional)
- [ ] Question difficulty levels
- [ ] Performance analytics
- [ ] Multi-language support
- [ ] Mobile app

## Development

### Adding New Features

1. Add functionality to `app/main.py`
2. Write tests in `tests/test_main.py`
3. Run tests: `pytest tests/ -v`
4. Update documentation

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings
- Comment complex logic

### Testing Requirements

- Minimum 80% code coverage
- All edge cases covered
- Integration tests for workflows

## License

MIT License - See LICENSE file

## Support

For issues or questions:
1. Check troubleshooting section
2. Review test cases for usage examples
3. Check code comments for implementation details

## Contributors

- Muthoni Gathiithi - Initial development

---

**Last Updated**: DEC 1 , 2025
**Version**: 0.1.0 (MVP)
